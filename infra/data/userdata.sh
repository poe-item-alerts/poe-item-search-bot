#!/bin/bash

yum install git docker -y
sudo service docker start
git clone https://github.com/poe-item-alerts/poe-item-search-bot.git
cd poe-item-search-bot
docker build -t poe-item-search-bot .
export DISCORD_TOKEN=$(aws ssm get-parameter --name "/poe-item-alerts/discord-token" --query Parameter.Value --output text --region "eu-central-1")
docker run -e DISCORD_TOKEN=$DISCORD_TOKEN poe-item-search-bot:latest
