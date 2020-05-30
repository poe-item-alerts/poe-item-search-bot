import logging
import os
import time
import json
import itertools

import boto3

from operator import itemgetter

from discord import Embed
from discord.ext import commands

from util import match_player_to_acc


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("poe_item_search_bot")
if os.environ.get("LOG_LEVEL"):
    logger.setLevel(os.environ["LOG_LEVEL"])
else:
    logger.setLevel("INFO")

bot = commands.Bot(command_prefix="!item-alert ")


@bot.command()
async def find(ctx, *args):
    logging.info(f"Got alert event: {args}")
    client = boto3.client("lambda", region_name="eu-central-1")
    start_time = time.perf_counter()
    # expect something like type:TypeName or mod:ModValue
    if args:
        filters = []
        for arg in args:
            filter_types = arg.split(":")[0].split("+")
            filter_values = arg.split(":")[1].split("+")
            tmp = {}
            for filter_type, filter_value in zip(filter_types, filter_values):
                tmp[filter_type] = filter_value
            filters.append(tmp)
        logger.debug(f"Created filter list: {filters}")
    for f in filters:
        f_name = list(f.keys())[0]
        f_val = list(f.values())[0]
        title = f"{f_name} | {f_val}"
        payload = {
            "filter": f
        }
        logger.debug(f"Invoking lambda for all items with {payload}")
        resp = client.invoke(
            FunctionName="poe_item_search",
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )
        result = json.loads(resp["Payload"].read().decode("utf-8"))
        logger.debug(f"Lambda ran successfully!")
        players = {}
        for player in result:
            logger.debug(f"Adding {player['account_name']} to message...")
            players[player["account_name"]] = []
        for player in result:
            players[player["account_name"]].append(
                {
                    "item_line": player["item"],
                    "created": player["created"],
                    "inventory_id": player["inventory_id"]
                }
            )
        message = Embed(title=title)
        for player, items in players.items():
            known_player = match_player_to_acc(player)
            if known_player:
                player= known_player
            result_items = []
            items = sorted(items, key=itemgetter("inventory_id"))
            for key, value in itertools.groupby(items, key=itemgetter("inventory_id")):
                tmp = sorted(list(value), key=itemgetter("created"), reverse=True)[0]
                result_items.append(tmp["item_line"])
            # for item in items:
            #     result_item = item["item_line"]
            #     for i in items:
            #         if item["inventory_id"] == i["inventory_id"]:
            #             if item["created"] < i["created"]:
            #                 result_item = i["item_line"]

            if len(message.fields) == 25:
                await ctx.send(embed=message)
                message = Embed(title=title)
            message.add_field(
                name=player,
                value=", ".join(result_items),
                inline=True,
            )
        else:
            await ctx.send(embed=message)

        stop_time = time.perf_counter()
        duration = f"{stop_time - start_time:0.2f}"
        message.add_field(name="Duration", value=f"{duration}s", inline=False)
        logger.debug(f"Sending message...")
        logger.debug(f"Ran query in {duration} seconds")


@bot.command()
async def set_league(ctx, league_name):
    client = boto3.client("ssm", region_name="eu-central-1")
    logger.debug(f"Got set_league event {ctx}")
    client.put_parameter(
        Name="/poe-item-alerts/character-load/ladders",
        Value=league_name,
        Type="String",
        Overwrite=True
    )
    await ctx.send(f"Set active league: {league_name}")


@bot.command()
async def get_league(ctx):
    client = boto3.client("ssm", region_name="eu-central-1")
    logger.debug(f"Got get_league event {ctx}")
    resp = client.get_parameter(Name="/poe-item-alerts/character-load/ladders")
    league = resp["Parameter"]["Value"]
    await ctx.send(f"Current active league: {league}")


@bot.command()
async def cfg_ingest(ctx, status):
    ssm = boto3.client("ssm", region_name="eu-central-1")
    admin_id = client.get_paramter(Name="/poe-item-alerts/admin-id")["Parameter"]["Value"]
    if ctx.message.author.id == int(admin_id):
        client = boto3.client("events", region_name="eu-central-1")
        if status == "enable":
            client.enable_rule(Name="poe_ladder_exporter")
            await ctx.send("Enabled ingestion!")
        elif status == "disable":
            client.disable_rule(Name="poe_ladder_exporter")
            await ctx.send("Disabled ingestion!")
        else:
            await ctx.send("Didn't recognise the status please use either 'enable' or 'disable'")
            

bot.run(os.environ["DISCORD_TOKEN"])
