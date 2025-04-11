# AWS 3-Tier Infrastructure Project - Terraform

This project sets up a complete 3-tier AWS infrastructure using Terraform, consisting of:

- VPC with public and private subnets
- EC2 instances for the application tier
- RDS database for the data tier
- Associated security groups and networking components

## Prerequisites

Before you begin, ensure you have the following installed:

- [Terraform](https://www.terraform.io/downloads.html) (v1.0.0 or newer)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [Git](https://git-scm.com/downloads) (optional, for version control)

## Project Structure

```
aws-infra-project-terraform/
├── modules/
│   ├── ec2/                # EC2 instance configuration
│   ├── rds/                # RDS database configuration
│   └── vpc/                # VPC and networking configuration
├── .terraform/
│   └── environments/
│       └── dev/            # Development environment configuration
├── create_architecture_diagram.py    # Diagram generation script
├── requirements.txt        # Python dependencies for diagram generation
└── README.md              # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aws-infra-project-terraform
```

### 2. Configure AWS Credentials

Ensure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3. Initialize Terraform

Navigate to the environment directory:

```bash
cd .terraform/environments/dev
```

Initialize Terraform:

```bash
terraform init
```

### 4. Create a terraform.tfvars File

Create a `terraform.tfvars` file to set your variables:

```bash
cat > terraform.tfvars << EOF
aws_region = "us-east-1"  # Change to your preferred region
db_password = "YourSecurePassword123!"
db_user = "admin"
db_name = "mydb"
EOF
```

### 5. Plan the Deployment

Review the changes that will be made:

```bash
terraform plan
```

### 6. Deploy the Infrastructure

Apply the Terraform configuration:

```bash
terraform apply
```

When prompted, type `yes` to confirm the deployment.

### 7. Access Your Resources

After deployment completes, Terraform will output important information such as:
- VPC ID
- EC2 instance public IP
- RDS endpoint

You can view these outputs at any time with:

```bash
terraform output
```

## Managing Your Infrastructure

### Updating Resources

After making changes to your Terraform files:

```bash
terraform plan  # Review changes
terraform apply  # Apply changes
```

### Destroying Resources

To tear down all resources when they're no longer needed:

```bash
terraform destroy
```

When prompted, type `yes` to confirm.

## Customization

### Changing AWS Region

Edit the `terraform.tfvars` file and update the `aws_region` value.

### Modifying Instance Types

Edit the EC2 module variables in `modules/ec2/variables.tf` to change instance types.

### Database Configuration

Adjust database settings in `modules/rds/variables.tf` and update your `terraform.tfvars` file accordingly.

## Troubleshooting

### Common Issues

1. **Credential Errors**: Ensure AWS credentials are properly configured
2. **Resource Limits**: Check if you've hit AWS service limits in your account
3. **Dependency Errors**: Make sure all module dependencies are correctly defined

### Getting Help

If you encounter issues:
1. Check Terraform logs for detailed error messages
2. Verify AWS permissions for your IAM user/role
3. Consult the [Terraform AWS Provider documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Architecture Diagrams

For information on generating architecture diagrams for this project, see the [Generating Architecture Diagrams](./DIAGRAMS.md) section.

## Security Notes

- The database password is marked as sensitive in Terraform
- Security groups are configured to restrict access appropriately
- Consider using AWS Secrets Manager for production database credentials

## License

[Specify your license information here]
