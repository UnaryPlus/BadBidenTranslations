import tweepy
import googletrans
import logging
import random
import time
import os
import re

class Bot(tweepy.Stream):
    def __init__(self, key, secret_key, token, secret_token, accounts):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger()
        self.translator = googletrans.Translator()

        auth = tweepy.OAuthHandler(key, secret_key)
        auth.set_access_token(token, secret_token)

        self.api = tweepy.API(auth)
        self.api.verify_credentials()
        self.accounts = accounts

        super().__init__(key, secret_key, token, secret_token)
        self.filter(follow=self.accounts)

    def bad_translation(self, text):
        languages = [random.choice(list(googletrans.LANGUAGES)) for i in range(5)]
        languages.append('en')
        for lang in languages:
            text = self.translator.translate(text, dest=lang).text
        return text

    def on_status(self, tweet):
        if str(tweet.author.id) not in self.accounts: return
        if hasattr(tweet, 'retweeted_status'): return
        if len(tweet.text) < 24: return

        try: tweet_text = tweet.extended_tweet['full_text']
        except: tweet_text = tweet.text
        tweet_text = re.sub(r'http\S+', '', tweet_text)

        reply_text = '@' + tweet.author.screen_name + ' ' + self.bad_translation(tweet_text)
        self.logger.info('Tweet: ' + tweet_text)
        self.logger.info('Reply: ' + reply_text)

        try:
            time.sleep(120)
            reply = self.api.update_status(reply_text, in_reply_to_status_id=tweet.id)
            self.api.retweet(reply.id)
            self.logger.info('Reply was successful')
        except:
            self.logger.warning('Could not reply due to error')

def main():
    key = os.environ.get('KEY')
    secret_key = os.environ.get('SECRET_KEY')
    token = os.environ.get('TOKEN')
    secret_token = os.environ.get('SECRET_TOKEN')

    accounts = ['1349149096909668363', '939091']
    bot = Bot(key, secret_key, token, secret_token, accounts)

main()
