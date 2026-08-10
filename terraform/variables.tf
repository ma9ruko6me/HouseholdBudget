variable "aws_region" {
  description = "リソースを作成するAWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "リソース名のプレフィックスとして使うプロジェクト名"
  type        = string
  default     = "householdbudget"
}

variable "instance_type" {
  description = "EC2インスタンスタイプ(無料枠対象を指定すること)"
  type        = string
  default     = "t3.micro"
}

variable "allowed_cidr" {
  description = "SSH/HTTP接続を許可するCIDR。個人利用のみを想定するため0.0.0.0/0を許容している(CGNAT等でグローバルIPが変動する回線ではIP単位の絞り込みが機能しないため)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "db_instance_class" {
  description = "RDSインスタンスクラス(無料枠対象を指定すること)"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "アプリが使用するデータベース名"
  type        = string
  default     = "household_budget"
}

variable "db_username" {
  description = "RDSマスターユーザー名"
  type        = string
  default     = "household"
}

variable "repo_url" {
  description = "EC2上にcloneするアプリリポジトリのURL"
  type        = string
  default     = "https://github.com/ma9ruko6me/HouseholdBudget.git"
}

variable "repo_ref" {
  description = "cloneするブランチ/タグ"
  type        = string
  default     = "main"
}
