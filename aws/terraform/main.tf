# Configure AWS provider with least privilege IAM role
provider "aws" {
    region = "us-west-2"
    assume_role {
        role_arn = "arn:aws:iam::ACCOUNT_ID:role/TerraformAccess"
    }
}

# EKS cluster with encryption and private networking
module "eks" {
    source  = "terraform-aws-modules/eks/aws"
    version = "~> 19.0"

    cluster_name    = "ai-serving-cluster"
    cluster_version = "1.27"
    vpc_id          = module.vpc.vpc_id
    subnet_ids      = module.vpc.private_subnets

    # Critical for security: Enable KMS encryption for Kubernetes secrets
    cluster_encryption_config = [
        {
            provider_key_arn = aws_kms_key.eks.arn
            resources        = ["secrets"]
        }
    ]

    # Node group with spot instances for cost savings
    eks_managed_node_groups = {
        spot = {
            desired_capacity = 3
            max_capacity     = 10
            min_capacity     = 1
            instance_types   = ["m6i.large", "m5.large"]
            capacity_type    = "SPOT" # Saves ~70% compute costs
        }
    }
}

# KMS key for encrypting Kubernetes secrets
resource "aws_kms_key" "eks" {
    description             = "EKS Secret Encryption Key"
    deletion_window_in_days = 7
    enable_key_rotation     = true # Automatically rotate keys for security
}
