# RDS Module - main.tf

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
