resource "aws_instance" "web" {
    ami           = "ami-03ab4e8f1d88ce614" 
    instance_type = "t2.micro"
    tags = var.tags
    subnet_id = "subnet-67c8101d"
    vpc_security_group_ids = [aws_security_group.bot.id]
    iam_instance_profile = aws_iam_instance_profile.bot.arn
}


resource "aws_security_group" "bot" {
  name        = "poe_item_search_bot" 
  description = "Allowing https and no more!"
  vpc_id      = "vpc-404e9928" 
  tags = var.tags
}

resource "aws_security_group_rule" "https_ingress" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bot.id
}

resource "aws_security_group_rule" "all_egress" {
  type        = "egress"
  from_port   = 0
  to_port     = 0
  protocol    = "all"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.bot.id
}
