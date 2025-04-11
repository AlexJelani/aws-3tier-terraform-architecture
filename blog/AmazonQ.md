# Building a 3-Tier AWS Infrastructure with Terraform

## Introduction

In today's cloud-first world, Infrastructure as Code (IaC) has become essential for managing cloud resources efficiently. In this article, I'll walk you through creating a complete 3-tier AWS infrastructure using Terraform, one of the most popular IaC tools.

![Terraform and AWS logos](https://placeholder.com/terraform-aws-logos)

## What We'll Build

We'll create a production-ready 3-tier architecture consisting of:

1. **Networking Layer**: VPC, subnets, internet gateway, and route tables
2. **Application Layer**: EC2 instances with security groups
3. **Database Layer**: RDS MySQL instance in a private subnet

![3-Tier Architecture Diagram](https://placeholder.com/3-tier-architecture-diagram)

## Prerequisites

- AWS account with appropriate permissions
- Terraform installed (v1.0+)
- Basic understanding of AWS services
- AWS CLI configured with access credentials

## Project Structure

Our project follows a modular approach for better organization and reusability:

```
aws-infra-project-terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ec2/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── rds/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
```

## Step 1: Setting Up the Network Layer

The foundation of our infrastructure is the VPC module, which creates:

- A VPC with CIDR block 10.0.0.0/16
- Public subnet for our web servers
- Two private subnets for our database (RDS requires at least two subnets in different AZs)
- Internet gateway for public internet access
- Route tables for traffic management
- Security groups for network security

![VPC Architecture Diagram](https://placeholder.com/vpc-architecture)

Key parts of our VPC module:

```hcl
# Create a VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

# Create a public subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "public-subnet"
  }
}

# Create private subnets for the database
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "private-subnet"
  }
}
```

## Step 2: Deploying the Application Layer

Our application layer consists of EC2 instances in the public subnet:

![EC2 Instance Diagram](https://placeholder.com/ec2-instance)

```hcl
# Create an EC2 instance
resource "aws_instance" "web" {
  ami           = "ami-0a3c3a20c09d6f377" # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  subnet_id     = var.subnet_id
  key_name      = "my-ec2-key"
  
  vpc_security_group_ids = [aws_security_group.ec2.id]
  
  tags = {
    Name = "web-server"
  }
}
```

The security group allows:
- HTTP traffic (port 80) from anywhere
- SSH access (port 22) for administration
- All outbound traffic

## Step 3: Setting Up the Database Layer

For our data tier, we're using Amazon RDS MySQL in the private subnets:

![RDS Database Diagram](https://placeholder.com/rds-database)

```hcl
# Create an RDS instance
resource "aws_db_instance" "main" {
  allocated_storage    = 10
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  db_name              = var.db_name
  username             = var.db_user
  password             = var.db_password
  parameter_group_name = "default.mysql8.0"
  db_subnet_group_name = var.subnet_group
  vpc_security_group_ids = [var.security_group_id]
  skip_final_snapshot  = true
}
```

The database is protected by:
- Placement in private subnets (no public internet access)
- Security group that only allows traffic from the application tier

## Step 4: Putting It All Together

Our main.tf file connects all the modules:

```hcl
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
  vpc_id = module.vpc.vpc_id
}

module "rds" {
  source = "./modules/rds"
  
  db_password = var.db_password
  db_user = var.db_user
  db_name = var.db_name
  subnet_group = module.vpc.db_subnet_group_name
  security_group_id = module.vpc.db_security_group_id
}
```

## Deployment Steps

1. Clone the repository
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Review the plan:
   ```bash
   terraform plan -var="db_password=yourpassword" -var="db_user=admin" -var="db_name=mydb"
   ```
4. Apply the configuration:
   ```bash
   terraform apply -var="db_password=yourpassword" -var="db_user=admin" -var="db_name=mydb"
   ```

![Terraform Apply Output](https://placeholder.com/terraform-apply)

## Security Considerations

This infrastructure includes several security best practices:
- Database in private subnets with no public access
- Security groups with least privilege access
- Separation of concerns between tiers

For production environments, consider these additional enhancements:
- Implement a bastion host for secure SSH access
- Add NAT gateway for private subnet internet access
- Enable encryption for RDS storage
- Implement AWS WAF for web application protection

## Cost Optimization

The infrastructure uses cost-effective components:
- t2.micro EC2 instance (~$8.50/month)
- db.t3.micro RDS instance (~$15/month)
- Minimal storage allocations

For further cost optimization:
- Use Reserved Instances for predictable workloads
- Implement auto-scaling for variable loads
- Consider Aurora Serverless for variable database workloads

## Conclusion

In this article, we've built a complete 3-tier AWS infrastructure using Terraform. This approach provides several benefits:

- **Reproducibility**: The entire infrastructure can be recreated with a single command
- **Version Control**: Infrastructure changes can be tracked in Git
- **Modularity**: Components can be reused across projects
- **Documentation**: The code itself serves as documentation

The modular design allows for easy expansion and customization to meet specific requirements.

![Completed Infrastructure](https://placeholder.com/completed-infrastructure)

## Next Steps

To extend this project, consider:
- Adding an Application Load Balancer for high availability
- Implementing auto-scaling for the EC2 instances
- Setting up CloudWatch monitoring and alarms
- Adding a CI/CD pipeline for infrastructure changes

The complete code for this project is available on [GitHub](https://github.com/yourusername/aws-infra-project-terraform).

Happy infrastructure coding!
