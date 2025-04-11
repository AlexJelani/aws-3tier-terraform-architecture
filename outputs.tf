output "vpc_id" {
  value = module.vpc.vpc_id
  description = "The ID of the VPC"
}

output "subnet_id" {
  value = module.vpc.subnet_id
  description = "The ID of the public subnet"
}

output "db_subnet_id" {
  value = module.vpc.db_subnet_id
  description = "The ID of the private subnet for the database"
}

output "db_subnet_group_name" {
  value = module.vpc.db_subnet_group_name
  description = "The name of the database subnet group"
}

output "db_security_group_id" {
  value = module.vpc.db_security_group_id
  description = "The ID of the database security group"
}
