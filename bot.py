import tweepy
import googletrans
import logging
import random
import time
import os
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

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

    def valid_tweet(self, tweet):
        return (
            str(tweet.author.id) in self.accounts
            and not hasattr(tweet, 'retweeted_status')
            and len(tweet.text) >= 64
        )

    def get_text(self, tweet):
        try: text = tweet.extended_tweet['full_text']
        except: text = tweet.text
        return re.sub(r'http\S+', '', text)

    def screenshot(self, tweet):
        service = Service(executable_path='./chromedriver')
        driver = webdriver.Chrome(service=service)
        try:
            driver.get('https://twitter.com/twitter/statuses/' + str(tweet.id))
            element = WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.TAG_NAME, 'article')))
            element.screenshot('screenshot.png')
        except Exception as e: raise e
        finally: driver.quit()

    def on_status(self, tweet):
        if not self.valid_tweet(tweet): return
        self.screenshot(tweet)

        original = self.get_text(tweet)
        translation = self.bad_translation(original)
        self.logger.info('Original: ' + original)
        self.logger.info('Translation: ' + translation)

        try: self.api.update_status_with_media(translation, 'screenshot.png')
        except: self.logger.warning('Could not tweet')
        else: sys.exit()

def main():
    key = os.environ.get('KEY')
    secret_key = os.environ.get('SECRET_KEY')
    token = os.environ.get('TOKEN')
    secret_token = os.environ.get('SECRET_TOKEN')

    accounts = ['1349149096909668363', '939091']
    bot = Bot(key, secret_key, token, secret_token, accounts)

main()
