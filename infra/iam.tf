resource "aws_iam_role" "poe_item_search_bot" {
  name = "poe_item_search_bot"
  assume_role_policy = file("policies/ec2_assume_role.json") 
  tags = var.tags
}

resource "aws_iam_instance_profile" "bot" {
  name = "poe_item_search_bot"
  role = aws_iam_role.poe_item_search_bot.name
}

resource "aws_iam_policy" "poe_item_search_bot_execution" {
  name = "poe_item_search_bot"
  policy = file("policies/poe_item_search_bot.json") 
}

resource "aws_iam_role_policy_attachment" "poe_item_search_bot" {
  role       = aws_iam_role.poe_item_search_bot.name
  policy_arn = aws_iam_policy.poe_item_search_bot_execution.arn
}

resource "aws_iam_role_policy_attachment" "ssm_basic_stuff" {
  role       = aws_iam_role.poe_item_search_bot.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
