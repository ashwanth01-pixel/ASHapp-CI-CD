FROM python:3.11-slim

WORKDIR /app/backend

# Install dependencies for AWS CLI and unzip tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    groff \
    less \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app files
COPY backend/ .

# Copy frontend files to one level above backend folder, so ../frontend works
WORKDIR /app
COPY frontend/ frontend/

# Reset working dir back to backend for running app.py
WORKDIR /app/backend

EXPOSE 5000

CMD ["python", "app.py"]

