import logging
import os
import time
import json

import boto3

from discord import Embed
from discord.ext import commands


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
        message = Embed(title=title)
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
        for player in result:
            logger.debug(f"Adding {player['account_name']} to message...")
            message.add_field(
                name=player["account_name"],
                value=player["item"],
                inline=True,
            )
        stop_time = time.perf_counter()
        duration = f"{stop_time - start_time:0.2f}"
        message.add_field(name="Duration", value=f"{duration}s", inline=False)
        logger.debug(f"Sending message...")
        await ctx.send(embed=message)
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


bot.run(os.environ["DISCORD_TOKEN"])
