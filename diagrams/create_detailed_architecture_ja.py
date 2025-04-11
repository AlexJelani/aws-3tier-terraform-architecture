#!/usr/bin/env python3
"""
詳細な日本語版AWS 3層アーキテクチャ図をPython Diagramsライブラリを使用して生成する
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC, PrivateSubnet, PublicSubnet, InternetGateway, RouteTable
# SecurityGroupは利用できないため、代わりにShieldを使用
from diagrams.aws.security import Shield
from diagrams.onprem.client import User

# 設定
output_file_name = "aws_3tier_detailed_architecture_ja"
show_diagram = True

# カスタム属性を持つ図の作成
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

with Diagram("AWS 3層アーキテクチャ", 
             filename=output_file_name, 
             show=show_diagram,
             direction="TB",  # TB = 上から下
             graph_attr=graph_attr,
             node_attr=node_attr,
             edge_attr=edge_attr):
    
    # 外部ユーザー
    user = User("ユーザー")
    
    # インターネットゲートウェイ
    igw = InternetGateway("インターネット\nゲートウェイ")
    
    # メインVPC
    with Cluster("VPC (10.0.0.0/16)"):
        
        # パブリックサブネット
        with Cluster("パブリックサブネット (10.0.1.0/24)\nアベイラビリティゾーン A"):
            public_rt = RouteTable("パブリック\nルートテーブル")
            # SecurityGroupの代わりにShieldを使用
            web_sg = Shield("Webセキュリティグループ\nポート: 80, 22")
            
            # Webサーバー
            web = EC2("Webサーバー\nt2.micro\nAmazon Linux 2")
        
        # データベース用プライベートサブネット
        with Cluster("データベース層 - プライベートサブネット"):
            # プライベートサブネット1
            with Cluster("プライベートサブネット1 (10.0.2.0/24)\nアベイラビリティゾーン B"):
                private_subnet1 = PrivateSubnet("プライベート\nサブネット1")
                
            # プライベートサブネット2
            with Cluster("プライベートサブネット2 (10.0.3.0/24)\nアベイラビリティゾーン C"):
                private_subnet2 = PrivateSubnet("プライベート\nサブネット2")
                
            # データベースセキュリティグループ
            # SecurityGroupの代わりにShieldを使用
            db_sg = Shield("データベースセキュリティグループ\nポート: 3306")
            
            # RDSインスタンス
            db = RDS("MySQL 8.0 データベース\ndb.t3.micro\n10GBストレージ")
    
    # ラベル付き接続
    user >> Edge(label="HTTP/SSH") >> igw
    igw >> Edge(label="トラフィックフロー") >> public_rt
    public_rt >> web_sg
    web_sg >> web
    web >> Edge(label="MySQL\nポート3306") >> db_sg
    db_sg >> db
    
    # データベースを両方のプライベートサブネットに接続（視覚的な表現のみ）
    db - Edge(style="dashed") - private_subnet1
    db - Edge(style="dashed") - private_subnet2

print(f"詳細なアーキテクチャ図が作成されました: {output_file_name}.png")
