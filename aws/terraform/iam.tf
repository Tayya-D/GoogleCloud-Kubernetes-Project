# IAM role for EKS nodes with least privilege
resource "aws_iam_role" "eks_nodes" {
    name = "eks-node-group-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
        Effect = "Allow"
        Principal = {
            Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        }]
    })
}

# Minimal policies for nodes
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
    policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
    role       = aws_iam_role.eks_nodes.name
}