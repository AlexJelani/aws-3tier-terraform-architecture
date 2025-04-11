#!/usr/bin/env python3
"""
日本語版AWS 3層アーキテクチャ図をPython Diagramsライブラリを使用して生成する
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, RouteTable
# SecurityGroupは利用できないため、代わりにShieldを使用
from diagrams.aws.security import Shield

# 設定
output_file_name = "aws_3tier_architecture_ja"
show_diagram = True

# 図の作成
with Diagram("AWS 3層アーキテクチャ", 
             filename=output_file_name, 
             show=show_diagram, 
             direction="TB"):  # TB = 上から下
    
    # インターネットゲートウェイ
    igw = InternetGateway("インターネット\nゲートウェイ")
    
    # メインVPC
    with Cluster("VPC (10.0.0.0/16)"):
        
        # パブリックサブネット
        with Cluster("パブリックサブネット (10.0.1.0/24)\nアベイラビリティゾーン A"):
            public_rt = RouteTable("パブリック\nルートテーブル")
            # SecurityGroupの代わりにShieldを使用
            web_sg = Shield("Webセキュリティ\nグループ")
            
            # Webサーバー
            web = EC2("Webサーバー\nt2.micro")
        
        # プライベートサブネット1
        with Cluster("プライベートサブネット1 (10.0.2.0/24)\nアベイラビリティゾーン B"):
            private_subnet1 = PrivateSubnet("プライベート\nサブネット1")
            
        # プライベートサブネット2
        with Cluster("プライベートサブネット2 (10.0.3.0/24)\nアベイラビリティゾーン C"):
            private_subnet2 = PrivateSubnet("プライベート\nサブネット2")
            
        # データベースセキュリティグループ
        # SecurityGroupの代わりにShieldを使用
        db_sg = Shield("データベース\nセキュリティグループ")
        
        # RDSインスタンス
        db = RDS("MySQLデータベース\ndb.t3.micro")
    
    # 接続
    igw >> public_rt >> web_sg >> web
    web >> db_sg >> db
    
    # データベースを両方のプライベートサブネットに接続（視覚的な表現のみ）
    db - private_subnet1
    db - private_subnet2

print(f"アーキテクチャ図が作成されました: {output_file_name}.png")
