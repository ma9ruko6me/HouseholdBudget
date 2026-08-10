resource "aws_instance" "app" {
  ami                         = data.aws_ami.amazon_linux_2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  key_name                    = aws_key_pair.ec2.key_name
  associate_public_ip_address = true

  user_data = templatefile("${path.module}/scripts/bootstrap.sh.tftpl", {
    database_url = "mysql+pymysql://${aws_db_instance.app.username}:${random_password.db_master.result}@${aws_db_instance.app.address}:${aws_db_instance.app.port}/${aws_db_instance.app.db_name}"
    repo_url     = var.repo_url
    repo_ref     = var.repo_ref
  })
  user_data_replace_on_change = true

  tags = {
    Name = "${var.project_name}-app"
  }
}
