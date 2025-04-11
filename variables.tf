# Define Input Variables

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
variable "db_password" {
  description = "Password for the RDS database"
  type        = string
  sensitive   = true
}

variable "db_user" {
  description = "Username for the RDS database"
  type        = string
  default     = "admin"
}

variable "db_name" {
  description = "Name of the RDS database"
  type        = string
  default     = "mydb"
}


