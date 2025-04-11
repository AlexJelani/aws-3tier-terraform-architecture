# Main Terraform Configuration

# Define provider
provider "aws" {
  region = var.aws_region
}

# Include modules
module "vpc" {
  source = "./modules/vpc"
  aws_region = var.aws_region
}

module "ec2" {
  source = "./modules/ec2"
  subnet_id = module.vpc.subnet_id
  vpc_id = module.vpc.vpc_id  # Add this line
}

module "rds" {
  source = "./modules/rds"
  
  db_password = var.db_password
  db_user = var.db_user
  db_name = var.db_name
  subnet_group = module.vpc.db_subnet_group_name
  security_group_id = module.vpc.db_security_group_id
}