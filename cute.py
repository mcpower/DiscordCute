import discord
import asyncio
import praw
import datetime

with open("token.txt") as token_file:
    TOKEN = token_file.read().strip()

r = praw.Reddit(user_agent="DiscordCute v0.1")
client = discord.Client()
loop = asyncio.get_event_loop()

approved_channels = set()


@asyncio.coroutine
def send_cute(channel, subreddit="aww"):
    yield from client.send_typing(channel)
    try:
        submission = r.get_random_submission(subreddit=subreddit)
        message = submission.title + "\n" + submission.url
    except praw.errors.InvalidSubreddit:
        message = "Invalid subreddit."
    yield from client.send_message(channel, message)


@asyncio.coroutine
def schedule_cute():
    today = datetime.datetime.utcnow()
    next_time = today.replace(hour=19, minute=0, second=0, microsecond=0)
    delta = datetime.timedelta(days=1)
    if next_time < today:
        next_time += delta

    while True:
        seconds = (next_time - datetime.datetime.utcnow()).total_seconds()
        next_time += delta
        print("Sleeping for", seconds, "seconds.")
        yield from asyncio.sleep(seconds)
        print("Woke up! Sending!")
        for channel in approved_channels:
            yield from send_cute(channel)


@client.event
@asyncio.coroutine
def on_ready():
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
@asyncio.coroutine
def on_message(message):
    if message.channel not in approved_channels:
        return

    if message.content.startswith('!cute'):
        subreddits = "+".join(message.content.split()[1:])
        if not subreddits:
            subreddits = "aww"
        yield from send_cute(message.channel, subreddits)

try:
    loop.run_until_complete(client.login(TOKEN))
    loop.run_until_complete(client.connect())
except KeyboardInterrupt:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
