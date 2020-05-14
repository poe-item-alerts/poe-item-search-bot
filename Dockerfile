FROM python:3.8.2

COPY src/discord_bot/requirements.txt requirements.txt

# Install all the deps
RUN pip install -r requirements.txt

COPY src/discord_bot .

CMD ["python", "bot.py"]


