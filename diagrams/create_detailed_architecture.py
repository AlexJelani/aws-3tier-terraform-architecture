#!/usr/bin/env python3
"""
Generate a detailed AWS 3-Tier Architecture Diagram using Python Diagrams library
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, RouteTable
# SecurityGroup is not available, so we'll use Shield instead
from diagrams.aws.security import Shield
from diagrams.onprem.client import User

# Configuration
output_file_name = "aws_3tier_detailed_architecture"
show_diagram = True

# Create the diagram with custom attributes
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5"
}

node_attr = {
    "fontsize": "14",
    "fontcolor": "#333333"
}

edge_attr = {
    "fontsize": "12"
}

with Diagram("AWS 3-Tier Architecture", 
             filename=output_file_name, 
             show=show_diagram,
             direction="TB",  # TB = Top to Bottom
             graph_attr=graph_attr,
             node_attr=node_attr,
             edge_attr=edge_attr):
    
    # External User
    user = User("User")
    
    # Internet Gateway
    igw = InternetGateway("Internet Gateway")
    
    # Main VPC
    with Cluster("VPC (10.0.0.0/16)"):
        
        # Public Subnet
        with Cluster("Public Subnet (10.0.1.0/24)\nAvailability Zone A"):
            public_rt = RouteTable("Public Route Table")
            # Using Shield instead of SecurityGroup
            web_sg = Shield("Web Security Group\nPorts: 80, 22")
            
            # Web Server
            web = EC2("Web Server\nt2.micro\nAmazon Linux 2")
        
        # Private Subnets for Database
        with Cluster("Database Tier - Private Subnets"):
            # Private Subnet 1
            with Cluster("Private Subnet 1 (10.0.2.0/24)\nAvailability Zone B"):
                private_subnet1 = PrivateSubnet("Private Subnet 1")
                
            # Private Subnet 2
            with Cluster("Private Subnet 2 (10.0.3.0/24)\nAvailability Zone C"):
                private_subnet2 = PrivateSubnet("Private Subnet 2")
                
            # Database Security Group
            # Using Shield instead of SecurityGroup
            db_sg = Shield("Database Security Group\nPort: 3306")
            
            # RDS Instance
            db = RDS("MySQL 8.0 Database\ndb.t3.micro\n10GB Storage")
    
    # Connections with labels
    user >> Edge(label="HTTP/SSH") >> igw
    igw >> Edge(label="Traffic Flow") >> public_rt
    public_rt >> web_sg
    web_sg >> web
    web >> Edge(label="MySQL\nPort 3306") >> db_sg
    db_sg >> db
    
    # Connect DB to both private subnets (visual only)
    db - Edge(style="dashed") - private_subnet1
    db - Edge(style="dashed") - private_subnet2

print(f"Detailed architecture diagram created: {output_file_name}.png")
