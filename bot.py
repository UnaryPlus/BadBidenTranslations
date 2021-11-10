import tweepy
import googletrans
import random
import time
import re

class Bot(tweepy.StreamListener):
    def __init__(self, api, accounts):
        self.translator = googletrans.Translator()
        self.api = api
        self.accounts = accounts
        # start streaming
        self.stream = tweepy.Stream(self.api.auth, self)
        self.start_stream()

    def start_stream(self):
        try:
            # filter tweets by account
            self.stream.filter(follow=self.accounts)
        except:
            # tweepy throws a timeout error every hour or so
            # i'm not sure why, but this keeps the program from halting
            print('streaming ended due to error')
            time.sleep(10)
            self.start_stream()

    def bad_translation(self, text):
        # choose five random languages
        languages = [random.choice(list(googletrans.LANGUAGES)) for i in range(5)]
        languages.append('en')
        # translate the text into each language
        for lang in languages:
            text = self.translator.translate(text, dest=lang).text
        return text

    def on_status(self, tweet):
        # the president must be the one who posted the tweet (not someone replying to him)
        if str(tweet.author.id) not in self.accounts: return
        # the tweet must not be a retweet or shorter than 24 characters
        if hasattr(tweet, 'retweeted_status'): return
        if len(tweet.text) < 24: return

        # get the full text of the post and remove image urls
        try: tweet_text = tweet.extended_tweet["full_text"]
        except: tweet_text = tweet.text
        tweet_text = re.sub(r'http\S+', '', tweet_text)
        # create the reply text and print it
        reply_text = '@' + tweet.author.screen_name + ' ' + self.bad_translation(tweet_text)
        print('tweet: ', tweet_text)
        print('reply: ', reply_text)

        try:
            # wait 2 minutes before replying
            time.sleep(120)
            # reply to the president's post and retweet the reply
            reply = self.api.update_status(reply_text, tweet.id)
            self.api.retweet(reply.id)
            print('reply was successful')
        except:
            print('could not reply due to error')

def main():
    # twitter api keys
    key = ...
    secret_key = ...
    token = ...
    secret_token = ...
    # create authentication
    auth = tweepy.OAuthHandler(key, secret_key)
    auth.set_access_token(token, secret_token)

    # connect to twitter api
    api = tweepy.API(auth)
    # account ids for @JoeBiden and @POTUS
    accounts = ['1349149096909668363', '939091']
    # start the bot
    Bot(api, accounts)

main()
