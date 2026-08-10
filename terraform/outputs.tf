output "instance_public_ip" {
  description = "EC2インスタンスのパブリックIP"
  value       = aws_instance.app.public_ip
}

output "ssh_connect_command" {
  description = "SSH接続コマンド"
  value       = "ssh -i ${local_sensitive_file.private_key.filename} ec2-user@${aws_instance.app.public_ip}"
}

output "db_endpoint" {
  description = "RDSエンドポイント(ホスト:ポート)"
  value       = aws_db_instance.app.endpoint
}

output "database_url" {
  description = "backendのDATABASE_URLに設定するSQLAlchemy接続文字列"
  value       = "mysql+pymysql://${aws_db_instance.app.username}:${random_password.db_master.result}@${aws_db_instance.app.address}:${aws_db_instance.app.port}/${aws_db_instance.app.db_name}"
  sensitive   = true
}

output "db_username" {
  description = "RDSマスターユーザー名"
  value       = aws_db_instance.app.username
}

output "db_password" {
  description = "RDSマスターパスワード"
  value       = random_password.db_master.result
  sensitive   = true
}
