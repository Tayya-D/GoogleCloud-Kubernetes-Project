# Isolated VPC with private subnets only
module "vpc" {
    source  = "terraform-aws-modules/vpc/aws"
    version = "~> 3.0"

    name = "ai-serving-vpc"
    cidr = "10.0.0.0/16"

    # No public subnets (security best practice)
    private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
    public_subnets  = []

    enable_nat_gateway = true  # Required for private subnets to access internet
}