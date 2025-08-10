variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ec2_ssh_key" {
  type    = string
  default = "ashwanthramnv"
}

variable "eks_cluster_name" {
  type    = string
  default = "ashapp-eks"
}

variable "eks_nodegroup_name" {
  type    = string
  default = "ashapp-node-group"
}

variable "eks_cluster_role_name" {
  type    = string
  default = "ashapp-eks-cluster-role"
}

variable "eks_nodegroup_role_name" {
  type    = string
  default = "ashapp-node-group-role"
}

variable "ecr_repo_name" {
  type    = string
  default = "ashapp-ecr"
}

