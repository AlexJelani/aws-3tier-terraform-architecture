---
title: Terraformを使用した本番環境対応の3層AWS インフラストラクチャの構築
published: false
description: Terraformを使用してVPC、EC2、RDSコンポーネントを含む完全な3層AWSアーキテクチャをセキュリティのベストプラクティスとともに作成する方法を学びましょう。
tags: aws, terraform, devops, infrastructure
cover_image: https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-cover-image.jpg
series: AWSインフラストラクチャ・アズ・コード
---

# Terraformを使用した本番環境対応の3層AWS インフラストラクチャの構築

![TerraformとAWSのロゴ](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-terraform-aws.jpg)

## はじめに

今日のクラウドファーストの世界では、Infrastructure as Code（IaC）がクラウドリソースを効率的に管理するために不可欠になっています。Terraformは最も人気のあるIaCツールの一つとして台頭し、開発者や運用チームがインフラストラクチャを宣言的に定義できるようになりました。

このチュートリアルでは、Terraformを使用して完全な3層AWSインフラストラクチャを作成する方法を説明します。このアーキテクチャは多くの本番アプリケーションに適しており、主要なAWSの概念とベストプラクティスを示しています。

## 構築するもの

以下の要素からなる本番環境対応の3層アーキテクチャを構築します：

1. **ネットワーキング層**：VPC、サブネット、インターネットゲートウェイ、ルートテーブル
2. **アプリケーション層**：セキュリティグループを持つEC2インスタンス
3. **データベース層**：プライベートサブネット内のRDS MySQLインスタンス

![3層アーキテクチャ図](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-3tier-diagram.jpg)

## 前提条件

始める前に、以下のものが必要です：

- 適切な権限を持つAWSアカウント
- Terraformがインストールされていること（v1.0以上）
- AWSサービスの基本的な理解
- アクセス認証情報で設定されたAWS CLI

## プロジェクト構造

プロジェクトは、より良い組織化と再利用性のためにモジュラーアプローチを採用しています：

```
aws-infra-project-terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ec2/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── rds/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
```

このモジュラー構造により、以下のことが可能になります：
- 関連するリソースをまとめて整理する
- 異なるプロジェクト間でモジュールを再利用する
- 関心事の分離が明確になり、よりクリーンなコードを維持する

## ステップ1：ネットワーク層の設定

インフラストラクチャの基盤はVPCモジュールであり、アプリケーションに必要なネットワークコンポーネントを作成します。

![VPCアーキテクチャ図](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-vpc-diagram.jpg)

VPCモジュールの主要コンポーネントを見てみましょう：

```hcl
# VPCの作成
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

# パブリックサブネットの作成
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "public-subnet"
  }
}

# データベース用のプライベートサブネットの作成
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "private-subnet"
  }
}

# もう一つのプライベートサブネットの作成（RDSには異なるAZに少なくとも2つのサブネットが必要）
resource "aws_subnet" "private2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}c"

  tags = {
    Name = "private-subnet-2"
  }
}

# インターネットゲートウェイの作成
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# パブリックサブネット用のルートテーブルの作成
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-route-table"
  }
}
```

これにより以下が作成されます：
- CIDRブロック10.0.0.0/16のVPC
- Webサーバー用のパブリックサブネット
- データベース用の2つのプライベートサブネット（RDSには異なるAZに少なくとも2つのサブネットが必要）
- パブリックインターネットアクセス用のインターネットゲートウェイ
- トラフィック管理用のルートテーブル

## ステップ2：アプリケーション層のデプロイ

アプリケーション層は、パブリックサブネット内のEC2インスタンスで構成されています：

![EC2インスタンス図](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-ec2-diagram.jpg)

```hcl
# EC2インスタンス用のセキュリティグループの作成
resource "aws_security_group" "ec2" {
  name        = "ec2-security-group"
  description = "EC2インスタンス用のセキュリティグループ"
  vpc_id      = var.vpc_id
  
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

# EC2インスタンスの作成
resource "aws_instance" "web" {
  ami           = "ami-0a3c3a20c09d6f377" # Amazon Linux 2 AMI
  instance_type = "t2.micro"
  subnet_id     = var.subnet_id
  key_name      = "my-ec2-key"
  
  vpc_security_group_ids = [aws_security_group.ec2.id]
  
  tags = {
    Name = "web-server"
  }
}
```

セキュリティグループは以下を許可します：
- どこからでもHTTPトラフィック（ポート80）
- 管理用のSSHアクセス（ポート22）
- すべての送信トラフィック

## ステップ3：データベース層の設定

データ層には、プライベートサブネット内のAmazon RDS MySQLを使用しています：

![RDSデータベース図](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-rds-diagram.jpg)

```hcl
# RDSインスタンスの作成
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
```

データベースは以下によって保護されています：
- パブリックインターネットアクセスのないプライベートサブネットへの配置
- アプリケーション層からのトラフィックのみを許可するセキュリティグループ

## ステップ4：すべてをまとめる

main.tfファイルはすべてのモジュールを接続します：

```hcl
# メインTerraform設定

# プロバイダーの定義
provider "aws" {
  region = var.aws_region
}

# モジュールの組み込み
module "vpc" {
  source = "./modules/vpc"
  aws_region = var.aws_region
}

module "ec2" {
  source = "./modules/ec2"
  subnet_id = module.vpc.subnet_id
  vpc_id = module.vpc.vpc_id
}

module "rds" {
  source = "./modules/rds"
  
  db_password = var.db_password
  db_user = var.db_user
  db_name = var.db_name
  subnet_group = module.vpc.db_subnet_group_name
  security_group_id = module.vpc.db_security_group_id
}
```

## デプロイ手順

それでは、インフラストラクチャをデプロイしましょう：

1. リポジトリをクローンします：
   ```bash
   git clone https://github.com/yourusername/aws-infra-project-terraform.git
   cd aws-infra-project-terraform
   ```

2. Terraformを初期化します：
   ```bash
   terraform init
   ```

3. プランを確認します：
   ```bash
   terraform plan -var="db_password=yourpassword" -var="db_user=admin" -var="db_name=mydb"
   ```

4. 設定を適用します：
   ```bash
   terraform apply -var="db_password=yourpassword" -var="db_user=admin" -var="db_name=mydb"
   ```

![Terraform適用出力](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-terraform-apply.jpg)

## セキュリティに関する考慮事項

このインフラストラクチャには、いくつかのセキュリティのベストプラクティスが含まれています：
- パブリックアクセスのないプライベートサブネット内のデータベース
- 最小権限アクセスを持つセキュリティグループ
- 層間の関心事の分離

本番環境では、以下の追加の強化を検討してください：
- 安全なSSHアクセスのためのバスティオンホストの実装
- プライベートサブネットのインターネットアクセス用のNATゲートウェイの追加
- RDSストレージの暗号化の有効化
- Webアプリケーション保護のためのAWS WAFの実装

## コスト最適化

このインフラストラクチャは、コスト効率の良いコンポーネントを使用しています：
- t2.micro EC2インスタンス（月額約8.50ドル）
- db.t3.micro RDSインスタンス（月額約15ドル）
- 最小限のストレージ割り当て

さらなるコスト最適化のために：
- 予測可能なワークロードにはリザーブドインスタンスを使用する
- 変動する負荷に対してはオートスケーリングを実装する
- 変動するデータベースワークロードにはAurora Serverlessの使用を検討する

## 結論

このチュートリアルでは、Terraformを使用して完全な3層AWSインフラストラクチャを構築しました。このアプローチにはいくつかの利点があります：

- **再現性**：インフラストラクチャ全体を単一のコマンドで再作成できる
- **バージョン管理**：インフラストラクチャの変更をGitで追跡できる
- **モジュール性**：コンポーネントをプロジェクト間で再利用できる
- **ドキュメント**：コード自体がドキュメントとして機能する

![完成したインフラストラクチャ](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/placeholder-completed-infrastructure.jpg)

## 次のステップ

このプロジェクトを拡張するために、以下を検討してください：
- 高可用性のためのApplication Load Balancerの追加
- EC2インスタンスのオートスケーリングの実装
- CloudWatchモニタリングとアラームの設定
- インフラストラクチャ変更のためのCI/CDパイプラインの追加

このプロジェクトの完全なコードは[GitHub](https://github.com/yourusername/aws-infra-project-terraform)で入手できます。

---

Terraformで実装したい他のAWSインフラストラクチャパターンはありますか？下のコメントで教えてください！

インフラストラクチャコーディングを楽しんでください！🚀
