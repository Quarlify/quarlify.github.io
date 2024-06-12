channel = input("Введите название Twitch канала: ")

import asyncio
from twitchio.ext import commands
from textblob import TextBlob
from collections import defaultdict
from googletrans import Translator

class Bot(commands.Bot):

    def __init__(self, channel):
        super().__init__(token='oauth:9107hyrnqod3wi07g7gbtn05j718tv', prefix='!', initial_channels=[channel])
        self.karma = defaultdict(int)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.author.name.lower() in ['streamelements', 'nightbot', 'moobot']:
            return

        print(message.author.name, ": ", message.content)
        
        translated_message = translate_message(message.content)
        print('Переведено:', translated_message)
        
        sentiment_score = analyze_sentiment(translated_message)
        self.karma[message.author.name] += sentiment_score * 100
        print(message.author.name, ' прибавляется ', sentiment_score * 100)

        update_karma_file(self.karma, "karma_table.txt")
        print('Обновлено в karma_table.txt')

    async def _join_channel(self, channel_name):
        channel = self.get_channel(channel_name)
        if channel is None:
            print(f"Failed to find channel {channel_name}")
            exit()
        await channel.join()
        print('Подключен к каналу ', channel_name)

def translate_message(message):
    translator = Translator()
    translated_message = translator.translate(message, dest='en').text
    return translated_message

def analyze_sentiment(message):
    analysis = TextBlob(message)
    polarity = analysis.sentiment.polarity
    return polarity

def read_existing_karma(filename):
    karma = defaultdict(int)
    try:
        with open(filename, "r") as f:
            next(f)
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    user, karma_value = parts
                    karma[user] = int(karma_value)
    except (FileNotFoundError, ValueError):
        pass
    return karma

def update_karma_file(karma, filename):
    existing_karma = read_existing_karma(filename)
    for user, karma_value in karma.items():
        existing_karma[user] += karma_value

    with open(filename, "w") as f:
        f.write("User\tKarma\n")
        for user, karma_value in existing_karma.items():
            f.write(f"{user}\t{karma_value}\n")

def main():
    bot = Bot(channel)
    bot.run()

if __name__ == "__main__":
    main()
