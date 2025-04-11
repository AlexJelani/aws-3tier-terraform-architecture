#!/usr/bin/env python3
"""
Generate AWS 3-Tier Architecture Diagram using Python Diagrams library
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, RouteTable
# SecurityGroup is not available, so we'll use a different component
from diagrams.aws.security import Shield

# Configuration
output_file_name = "aws_3tier_architecture"
show_diagram = True

# Create the diagram
with Diagram("AWS 3-Tier Architecture", 
             filename=output_file_name, 
             show=show_diagram, 
             direction="TB"):  # TB = Top to Bottom
    
    # Internet Gateway
    igw = InternetGateway("Internet Gateway")
    
    # Main VPC
    with Cluster("VPC (10.0.0.0/16)"):
        
        # Public Subnet
        with Cluster("Public Subnet (10.0.1.0/24)\nAvailability Zone A"):
            public_rt = RouteTable("Public Route Table")
            # Using Shield instead of SecurityGroup
            web_sg = Shield("Web Security Group")
            
            # Web Server
            web = EC2("Web Server\nt2.micro")
        
        # Private Subnet 1
        with Cluster("Private Subnet 1 (10.0.2.0/24)\nAvailability Zone B"):
            private_subnet1 = PrivateSubnet("Private Subnet 1")
            
        # Private Subnet 2
        with Cluster("Private Subnet 2 (10.0.3.0/24)\nAvailability Zone C"):
            private_subnet2 = PrivateSubnet("Private Subnet 2")
            
        # Database Security Group
        # Using Shield instead of SecurityGroup
        db_sg = Shield("Database Security Group")
        
        # RDS Instance
        db = RDS("MySQL Database\ndb.t3.micro")
    
    # Connections
    igw >> public_rt >> web_sg >> web
    web >> db_sg >> db
    
    # Connect DB to both private subnets (visual only)
    db - private_subnet1
    db - private_subnet2

print(f"Architecture diagram created: {output_file_name}.png")
