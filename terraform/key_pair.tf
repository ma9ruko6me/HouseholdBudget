resource "tls_private_key" "ec2" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ec2" {
  key_name   = "${var.project_name}-key"
  public_key = tls_private_key.ec2.public_key_openssh
}

resource "local_sensitive_file" "private_key" {
  filename        = "${path.module}/generated/${var.project_name}-key.pem"
  content         = tls_private_key.ec2.private_key_pem
  file_permission = "0400"
}
