# EC2 Module - main.tf

# Create a security group for the EC2 instance
resource "aws_security_group" "ec2" {
  name        = "ec2-security-group"
  description = "Security group for EC2 instances"
  vpc_id      = var.vpc_id  # Add this line to specify the VPC
  
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
  # Use a current Amazon Linux 2 AMI
  ami           = "ami-0a3c3a20c09d6f377" # Amazon Linux 2 AMI for us-east-1
  instance_type = "t2.micro"
  subnet_id     = var.subnet_id
  key_name      = "my-ec2-key"  # Add this line
  
  vpc_security_group_ids = [aws_security_group.ec2.id]
  
  tags = {
    Name = "web-server"
  }
}