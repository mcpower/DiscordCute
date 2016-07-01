import discord
import asyncio
import praw
import datetime

TOKEN = open("token.txt").read().strip()

r = praw.Reddit(user_agent="DiscordCute v0.1")
subreddit = r.get_subreddit("aww")
client = discord.Client()
loop = asyncio.get_event_loop()

approved_channels = set()


async def send_cute(channel):
    submission = subreddit.get_random_submission()
    await client.send_message(channel, submission.title + "\n" + submission.url)


async def schedule_cute():
    today = datetime.datetime.utcnow()
    next_time = today.replace(hour=19, minute=0, second=0, microsecond=0)
    delta = datetime.timedelta(days=1)
    if next_time < today:
        next_time += delta

    while True:
        seconds = (next_time - datetime.datetime.utcnow()).total_seconds()
        next_time += delta
        print("Sleeping for", seconds, "seconds.")
        await asyncio.sleep(seconds)
        print("Woke up! Sending!")
        for channel in approved_channels:
            await send_cute(channel)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print("Getting approved channels...")

    for channel in client.get_all_channels():
        if channel.name.startswith("cute"):
            approved_channels.add(channel)

    print("Done!", len(approved_channels), "channels found")
    print("Beginning cute loop:")
    loop.create_task(schedule_cute())

@client.event
async def on_message(message):
    if message.channel not in approved_channels:
        return

    if message.content.startswith('!cute'):
        await send_cute(message.channel)

try:
    loop.run_until_complete(client.login(TOKEN))
    loop.run_until_complete(client.connect())
except KeyboardInterrupt:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
