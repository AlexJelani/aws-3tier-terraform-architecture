---
title: Building a Production-Ready 3-Tier AWS Infrastructure with Terraform
published: false
description: Learn how to create a complete 3-tier AWS architecture using Terraform, including VPC, EC2, and RDS components with security best practices.
tags: aws, terraform, devops, infrastructure
cover_image: https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-cover-image.jpg
series: AWS Infrastructure as Code
---

# Building a Production-Ready 3-Tier AWS Infrastructure with Terraform

![Terraform and AWS logos](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-terraform-aws.jpg)

## Introduction

In today's cloud-first world, Infrastructure as Code (IaC) has become essential for managing cloud resources efficiently. Terraform has emerged as one of the most popular IaC tools, allowing developers and operations teams to define infrastructure in a declarative way.

In this tutorial, I'll walk you through creating a complete 3-tier AWS infrastructure using Terraform. This architecture is suitable for many production applications and demonstrates key AWS concepts and best practices.

## What We'll Build

We'll create a production-ready 3-tier architecture consisting of:

1. **Networking Layer**: VPC, subnets, internet gateway, and route tables
2. **Application Layer**: EC2 instances with security groups
3. **Database Layer**: RDS MySQL instance in a private subnet

![3-Tier Architecture Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-3tier-diagram.jpg)

## Prerequisites

Before we begin, make sure you have:

- An AWS account with appropriate permissions
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

This modular structure allows us to:
- Organize related resources together
- Reuse modules across different projects
- Maintain cleaner code with better separation of concerns

## Step 1: Setting Up the Network Layer

The foundation of our infrastructure is the VPC module, which creates the networking components needed for our application.

![VPC Architecture Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-vpc-diagram.jpg)

Let's look at the key components of our VPC module:

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

# Create another private subnet (RDS requires at least 2 subnets in different AZs)
resource "aws_subnet" "private2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}c"

  tags = {
    Name = "private-subnet-2"
  }
}

# Create an internet gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# Create a route table for the public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-route-table"
  }
}
```

This creates:
- A VPC with CIDR block 10.0.0.0/16
- A public subnet for our web servers
- Two private subnets for our database (RDS requires at least two subnets in different AZs)
- An internet gateway for public internet access
- Route tables for traffic management

## Step 2: Deploying the Application Layer

Our application layer consists of EC2 instances in the public subnet:

![EC2 Instance Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-ec2-diagram.jpg)

```hcl
# Create a security group for the EC2 instance
resource "aws_security_group" "ec2" {
  name        = "ec2-security-group"
  description = "Security group for EC2 instances"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

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

![RDS Database Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-rds-diagram.jpg)

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

Now let's deploy our infrastructure:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aws-infra-project-terraform.git
   cd aws-infra-project-terraform
   ```

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

![Terraform Apply Output](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-terraform-apply.jpg)

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

In this tutorial, we've built a complete 3-tier AWS infrastructure using Terraform. This approach provides several benefits:

- **Reproducibility**: The entire infrastructure can be recreated with a single command
- **Version Control**: Infrastructure changes can be tracked in Git
- **Modularity**: Components can be reused across projects
- **Documentation**: The code itself serves as documentation

![Completed Infrastructure](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-completed-infrastructure.jpg)

## Next Steps

To extend this project, consider:
- Adding an Application Load Balancer for high availability
- Implementing auto-scaling for the EC2 instances
- Setting up CloudWatch monitoring and alarms
- Adding a CI/CD pipeline for infrastructure changes

The complete code for this project is available on [GitHub](https://github.com/yourusername/aws-infra-project-terraform).

---

What other AWS infrastructure patterns would you like to see implemented with Terraform? Let me know in the comments below!

Happy infrastructure coding! 🚀
