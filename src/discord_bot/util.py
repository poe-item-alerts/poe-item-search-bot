import logging

import yaml

logger = logging.getLogger("poe_item_search_bot.util")


def match_player_to_acc(account_name):
    with open("account_config.yml") as f:
        config = yaml.safe_load(f)
    if config["players"].get(account_name):
        return config["players"][account_name]
    else:
        return ""


def load_config():
    with open("account_config.yml") as f:
        config = yaml.safe_load(f)
    return config
