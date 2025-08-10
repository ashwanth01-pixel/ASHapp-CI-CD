import boto3
import subprocess
import json
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            output TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_to_history(query, output):
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (query, output, timestamp) VALUES (?, ?, ?)",
                   (query, output, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT query, output, timestamp FROM history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"query": r[0], "output": r[1], "timestamp": r[2]} for r in rows]

def ask_bedrock(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )

    result = json.loads(response['body'].read())
    return result['content'][0]['text'].strip()

def run_command_from_claude(prompt):
    command_prompt = (
        f'You are an expert in AWS CLI. Your job is to return only a valid, complete, and working AWS CLI command '
        f'in a single line based on the user’s request: "{prompt}". '
        f'Do not include explanations, line breaks, placeholders, or comments. '
        f'Always include the correct parameters such as region, resource IDs, and names. '
        f'Use common defaults (like region us-east-1, t2.micro, Amazon Linux 2023 kernel-6.1 AMI, '
        f'security group always use:-sg-083cd817b13d667d1, key pair name ashwanthramnv ) if not specified. '
        f'The output must only be a single-line AWS CLI command that can run without errors.'
    )

    command = ask_bedrock(command_prompt)

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return command, output.decode()
    except subprocess.CalledProcessError as e:
        return command, e.output.decode()

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/ask", methods=["POST"])
def api_handler():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    action = query.lower()
    if any(word in action for word in ["create", "delete", "modify", "update"]):
        # Now return confirmation in same request (frontend handles it inside chat)
        return jsonify({"confirmation_needed": True, "query": query})

    command, output = run_command_from_claude(query)
    formatted_output = f"Command: {command}\n{output.strip()}"
    save_to_history(query, formatted_output)
    return jsonify({"confirmation_needed": False, "output": formatted_output})

@app.route("/api/confirm", methods=["POST"])
def api_confirm():
    data = request.get_json()
    query = data.get("query")
    decision = data.get("decision")

    if decision.lower() != "accept":
        return jsonify({"output": "Action declined."})

    command, output = run_command_from_claude(query)
    formatted_output = f"Command: {command}\n{output.strip()}"
    save_to_history(query, formatted_output)
    return jsonify({"output": formatted_output})

@app.route("/api/history", methods=["GET"])
def api_history():
    return jsonify(get_history())

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

