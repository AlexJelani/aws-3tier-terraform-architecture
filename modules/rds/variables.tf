# RDS Variables

variable "instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the RDS database"
  type        = string
}

variable "db_user" {
  description = "Username for the RDS database"
  type        = string
}

variable "db_password" {
  description = "Password for the RDS database"
  type        = string
  sensitive   = true
}

variable "security_group_id" {
  description = "The ID of the security group for the database"
  type        = string
}

variable "subnet_group" {
  description = "The DB subnet group name"
  type        = string
}