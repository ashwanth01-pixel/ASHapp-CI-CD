output "ecr_repository_url" {
  value = aws_ecr_repository.ashapp.repository_url
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.ashapp.endpoint
}

output "eks_cluster_name" {
  value = aws_eks_cluster.ashapp.name
}

