import json
import time
from abc import ABC
from datetime import datetime
from enum import Enum
from threading import Thread

import requests
from bs4 import BeautifulSoup
from pytz import timezone
from requests_html import HTMLSession
from pyppeteer.errors import TimeoutError
from discord import Webhook, RequestsWebhookAdapter


#############################################################################################################
#                                       2020-11-16                                                          #
#   This script was made to check the stock of the PS5 console on some retailers websites.                  #
#   This works only for Canadians retailers                                                                 #
#   Number of retailers : 5                                                                                 #
#   Retailers supported as of now : TheSource, BestBuy Canada, Amazon Canada, Walmart Canada, EB Games      #
#   author            : youpi0214                                                                           #
#   name              : PS5Bot                                                                              #
#   version           : 3.0                                                                                 #
#   last modification : 2020-12-28                                                                          #
#############################################################################################################


class PS5Urls(Enum):
    BESTBUY_DIGITAL = 'https://www.bestbuy.ca/en-ca/product/playstation-5-digital-edition-console-online-only/14962184'
    BESTBUY_DIGITAL_REQUEST = 'https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.standardproduct.v1%2Bjson&accept-language=en-CA&locations=907%7C906&postalCode=G6V7P5&skus=14962184'
    BESTBUY_DISC = 'https://www.bestbuy.ca/en-ca/product/playstation-5-console-online-only/14962185'
    BESTBUY_DISC_REQUEST = 'https://www.bestbuy.ca/ecomm-api/availability/products?accept=application%2Fvnd.bestbuy.standardproduct.v1%2Bjson&accept-language=en-CA&locations=907%7C906&postalCode=G6Y9G6&skus=14962185'

    LASOURCE_DIGITAL = 'https://www.thesource.ca/en-ca/gaming/playstation/ps5/playstation%c2%ae5-digital-edition-console/p/108090498'
    LASOURCE_DISC = 'https://www.thesource.ca/en-ca/gaming/playstation/ps5/playstation%c2%ae5-console/p/108090499'

    EBGAMES_DIGITAL = 'https://www.ebgames.ca/PS5/Games/877523/playstation-5-digital-edition#'
    EBGAMES_DISC = 'https://www.ebgames.ca/PS5/Games/877522/playstation-5'

    WAL_AMZ = 'https://www.nowinstock.net/ca/videogaming/consoles/sonyps5/'

    AMAZON_DIGITAL = 'https://www.amazon.ca/dp/B08GS1N24H?tag=nowinet-20&linkCode=ogi&th=1&psc=1'
    AMAZON_DISC = 'https://www.amazon.ca/Playstation-3005721-PlayStation-Digital-Edition/dp/B08GSC5D9G/ref=sr_1_3?dchild=1&keywords=ps5&qid=1605143545&sr=8-3&th=1'

    WALMART_DIGITAL = 'https://www.walmart.ca/en/ip/playstation5-digital-edition/6000202198823'
    WALMART_DISC = 'https://www.walmart.ca/en/ip/playstation5-console/6000202198562'


class WebSites(ABC, Thread):
    TIMEZONE = 'EST'
    messageHead = 'PS5 available at '
    out_of_stock = ' PS5s currently went out of stock at '
    errorMessageHead = 'An error occurred '
    sleepTime = 15
    url_digit = None
    url_disc = None
    tries = 0
    triesCheckPoint = 3
    retailer = None
    checkedClass_digital = None
    checkedClass_disc = None
    keyWords = None
    # 1 = by class 2 = by id
    checkMethod = None
    DIGITAL_NAME = 'PS5 Digital '
    DISC_NAME = 'PS5 Disc '
    was_in_stock = False

    def __init__(self, pUrl_digital, pUrl_disc, pRetailer, pCheckedClass_digital, pCheckedClass_disc, pKeyWords,
                 pCheckMethod):
        super().__init__()
        self.name = pRetailer
        self.url_digit = pUrl_digital.value
        self.url_disc = pUrl_disc.value
        self.retailer = pRetailer
        self.checkedClass_digital = pCheckedClass_digital
        self.checkedClass_disc = pCheckedClass_disc
        self.keyWords = pKeyWords
        self.checkMethod = pCheckMethod

    # increment the number of tries to find available PS5 units
    def increTry(self):
        self.tries += 1
        if self.tries % self.triesCheckPoint == 0 or self.tries == 1:
            print(str(datetime.now(tz=timezone(self.TIMEZONE)).strftime(
                '%Y-%m-%d %H:%M:%S')) + ' ' + self.TIMEZONE + ' -- thread ' + self.name + ' - Attempt :',
                  self.tries)

    def notif(self, message, messageType):
        global PS5_DISCORD_HOOK_BUG_REPORT
        # alert me about a bug
        PS5_DISCORD_HOOK_BUG_REPORT.send(message);

    def publishAvailability(self, availability):
        global PS5_DISCORD_HOOK

        # send alert to every to everyone
        PS5_DISCORD_HOOK.send(availability)

        # TODO for testing only (publishAvailability)

    def startWebsiteSpying(self):
        digitalInStock = False
        discInStock = False
        while not digitalInStock or not discInStock:
            try:
                if isinstance(self, Amazon):
                    pass
                else:
                    html_digital = requests.get(self.url_digit)
                    soup_digital = BeautifulSoup(html_digital.content, 'html.parser')

                    html_disc = requests.get(self.url_disc)
                    soup_disc = BeautifulSoup(html_disc.content, 'html.parser')

                # This whole block check if the console is available to order online at a retailer
                if isinstance(self, Amazon):
                    digitalInStock = str(DIGIT_AMZ_RESULT).__contains__(self.keyWords)
                    discInStock = str(DISK_AMZ_RESULT).__contains__(self.keyWords)
                else:
                    try:
                        digitalInStock = str(soup_digital.find_all(class_=self.checkedClass_digital)[
                                                 0]).__contains__(self.keyWords) if self.checkMethod == 1 else str(
                            soup_digital.find_all(id=self.checkedClass_digital)[
                                0]).__contains__(self.keyWords)
                    except(IndexError):
                        # PS5 not available at retailer yet
                        pass

                    try:
                        discInStock = str(soup_disc.find_all(class_=self.checkedClass_disc)[
                                              0]).__contains__(self.keyWords) if self.checkMethod == 1 else str(
                            soup_disc.find_all(id=self.checkedClass_disc)[
                                0]).__contains__(self.keyWords)
                    except(IndexError):
                        # PS5 not available at retailer yet
                        pass

                if digitalInStock or discInStock:
                    self.was_in_stock = True
                    self.sleepTime = 40
                    digital_model = ''
                    disc_model = ''

                    if isinstance(self, LaSource):
                        digital_model = self.DIGITAL_NAME + '\nlink : ' + PS5Urls.LASOURCE_DIGITAL.value + '\n' if digitalInStock else ''
                        disc_model = self.DISC_NAME + '\nlink : ' + PS5Urls.LASOURCE_DISC.value if discInStock else ''
                    elif isinstance(self, EBGames):
                        digital_model = self.DIGITAL_NAME + '\nlink : ' + PS5Urls.EBGAMES_DIGITAL.value + '\n' if digitalInStock else ''
                        disc_model = self.DISC_NAME + '\nlink : ' + PS5Urls.EBGAMES_DISC.value if discInStock else ''
                    elif isinstance(self, Walmart):
                        digital_model = self.DIGITAL_NAME + '\nlink : ' + PS5Urls.WALMART_DIGITAL.value + '\n' if digitalInStock else ''
                        disc_model = self.DISC_NAME + '\nlink : ' + PS5Urls.WALMART_DISC.value if discInStock else ''
                    elif isinstance(self, Amazon):
                        digital_model = self.DIGITAL_NAME + '\nlink : ' + PS5Urls.AMAZON_DIGITAL.value + '\n' if digitalInStock else ''
                        disc_model = self.DISC_NAME + '\nlink : ' + PS5Urls.AMAZON_DISC.value if discInStock else ''
                    elif isinstance(self, BestBuy):
                        digital_model = self.DIGITAL_NAME + '\nlink : ' + PS5Urls.BESTBUY_DIGITAL.value + '\n' if digitalInStock else ''
                        disc_model = self.DISC_NAME + '\nlink : ' + PS5Urls.BESTBUY_DISC.value if discInStock else ''

                    message = str(datetime.now(tz=timezone(self.TIMEZONE)).strftime(
                        '%Y-%m-%d %H:%M:%S')) + ' ' + self.TIMEZONE + '\n\U0001F6A8**' + str(
                        self.messageHead) + self.retailer + '**\U0001F6A8' + '\nModel in stock :\n' + digital_model + disc_model + '\n@everyone'

                    self.publishAvailability(message)
                    digitalInStock = not digitalInStock
                    discInStock = not discInStock
                else:
                    self.handle_out_of_stock()
                    self.sleepTime = 15
                self.increTry()
                time.sleep(self.sleepTime)

            except(Exception) as exception:
                if isinstance(exception, TimeoutError):
                    pass
                else:
                    self.handleException(e=exception)

    def handle_out_of_stock(self):
        if self.was_in_stock:
            self.was_in_stock = False
            message = str(datetime.now(tz=timezone(self.TIMEZONE)).strftime(
                '%Y-%m-%d %H:%M:%S')) + ' ' + self.TIMEZONE + '\n**\U0001F61E' + str(
                self.out_of_stock) + self.retailer + '\U0001F61E**' + '\n@everyone'
            self.publishAvailability(message)

    def handleException(self, e):
        self.notif(
            str(datetime.now(tz=timezone(self.TIMEZONE)).strftime(
                '%Y-%m-%d %H:%M:%S')) + ' ' + self.TIMEZONE + '\n' + self.errorMessageHead + 'in Thread ' + self.name + ' -> ' + str(
                e),
            messageType=1)
        self.tries = 0
        time.sleep(self.sleepTime)


class LaSource(WebSites):
    NAME = 'LaSource'
    CLASS = 'button primary-button full-button addToCartButton'
    KEYWORDS = 'Add to Cart'
    CHECKMETHOD = 1

    def __init__(self, pUrl_digital, pUrl_disc):
        super().__init__(pUrl_digital, pUrl_disc, self.NAME, self.CLASS, self.CLASS, self.KEYWORDS, self.CHECKMETHOD)

    def run(self) -> None:
        super().startWebsiteSpying()


class EBGames(WebSites):
    NAME = 'EB Games'
    CLASS = 'megaButton cartAddRadio'
    KEYWORDS = 'display:block'
    CHECKMETHOD = 1

    def __init__(self, pUrl_digital, pUrl_disc):
        super().__init__(pUrl_digital, pUrl_disc, self.NAME, self.CLASS, self.CLASS, self.KEYWORDS, self.CHECKMETHOD)

    def run(self) -> None:
        super().startWebsiteSpying()


class Walmart(WebSites):
    NAME = 'Walmart'
    ID_DIGITAL = 'tr53045'
    ID_DISC = 'tr53026'

    KEYWORDS = 'In Stock'
    CHECKMETHOD = 2

    def __init__(self, pUrl_digital, pUrl_disc):
        super().__init__(pUrl_digital, pUrl_disc, self.NAME, self.ID_DIGITAL, self.ID_DISC, self.KEYWORDS,
                         self.CHECKMETHOD)

    def run(self) -> None:
        super().startWebsiteSpying()


class Amazon(WebSites):
    NAME = 'Amazon'
    PATH = '//*[@id="availability"]/span/text()[1]'
    KEYWORDS = 'In Stock'
    CHECKMETHOD = 2

    def __init__(self, pUrl_digital, pUrl_disc):
        super().__init__(pUrl_digital, pUrl_disc, self.NAME, self.PATH, self.PATH, self.KEYWORDS,
                         self.CHECKMETHOD)

    def run(self) -> None:
        super().startWebsiteSpying()


class BestBuy(WebSites):
    headers_digital = {
        'authority': 'www.bestbuy.ca',
        'pragma': 'no-cache',
        'cache-control': 'no-cache, no-store',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.bestbuy.ca/en-ca/product/playstation-5-digital-edition-console/14962184',
        'accept-language': 'en-US,en;q=0.9'
    }

    headers_disc = {
        'authority': 'www.bestbuy.ca',
        'pragma': 'no-cache',
        'cache-control': 'no-cache, no-store',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.bestbuy.ca/en-ca/product/playstation-5-console-online-only/14962185',
        'accept-language': 'en-US,en;q=0.9'
    }

    NAME = 'BestBuy'
    CLASS = None
    KEYWORDS = None
    CHECKMETHOD = None

    def __init__(self, pUrl_digital, pUrl_disc):
        super().__init__(pUrl_digital, pUrl_disc, self.NAME, self.CLASS, self.CLASS, self.KEYWORDS, self.CHECKMETHOD)

    def run(self) -> None:
        quantity_digital = 0
        quantity_disc = 0
        while (quantity_digital < 1 or quantity_disc < 1):
            try:
                response_digital = requests.get(url=self.url_digit, headers=self.headers_digital)
                response_digital_formatted = json.loads(response_digital.content.decode('utf-8-sig').encode('utf-8'))
                quantity_digital = response_digital_formatted['availabilities'][0]['shipping']['quantityRemaining']

                response_disc = requests.get(url=self.url_disc, headers=self.headers_disc)
                response_disc_formatted = json.loads(response_disc.content.decode('utf-8-sig').encode('utf-8'))
                quantity_disc = response_disc_formatted['availabilities'][0]['shipping']['quantityRemaining']

                if quantity_digital > 0 or quantity_disc > 0:
                    self.was_in_stock = True
                    # Send notification if In Stock then reset the quantity
                    digital_model = self.DIGITAL_NAME + ', Quantity : ' + str(
                        quantity_digital) + 'units' + '\nlink : ' + PS5Urls.BESTBUY_DIGITAL.value + '\n' if quantity_digital > 0 else ''
                    disc_model = self.DISC_NAME + ', Quantity : ' + str(
                        quantity_disc) + 'units' + '\nlink : ' + PS5Urls.BESTBUY_DISC.value if quantity_disc > 0 else ''

                    message = str(
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + self.TIMEZONE + '\n\U0001F6A8**' + str(
                        self.messageHead) + self.retailer + '**\U0001F6A8\n' + digital_model + disc_model + '\n@everyone'
                    self.publishAvailability(message)
                    print(message)
                    quantity_digital = 0
                    quantity_disc = 0
                    time.sleep(self.sleepTime)
                else:
                    self.handle_out_of_stock()
                    self.increTry()
                    time.sleep(self.sleepTime)

            except(Exception) as exception:
                self.handleException(e=exception)


SERVER_WELCOME = '\U0001F3AE **PS5_BotChecker 3.0** \U0001F3AE\nWelcome everyone!!' \
                 ' I Was designed to monitor both the digital and the disk version PS5 stock.\n' \
                 'I currently support Best Buy Canada, Amazon Canada(removed temporarily), TheSource and EBGames.' \
                 'Walmart support is still unstable for the moment.\n\nPS : follow https://twitter.com/lbabinz?s=21 ' \
                 'for optimal chances to secure a console. I work best on surprise drop.'

SERVER_START = '**Happy to coninuing work for you all!\nServer up and running... **\U0001F50E	 '

# Discord info
PS5_DISCORD_CHANNEL = 'https://discord.com/api/webhooks/792106841311150131/f-1Qu07gxa9X7ZoLZ3I8N29JoRUtQRtdZ_DjkTL4DHRFI0ZtBVEr02FB-45sJ-QmAzbj'
PS5_DISCORD_HOOK = None
PS5_DISCORD_BUG_REPORT_CHANNEL = 'https://discord.com/api/webhooks/792159555463151626/Lq4cpZbhVy4hmIoIotVppId6CCE0z3uu34AjH0PD1F3ZlTdP5Lbwq8jutBPhuXJ1GPPV'
PS5_DISCORD_HOOK_BUG_REPORT = None

DIGIT_AMZ_RESULT = ''
DISK_AMZ_RESULT = ''
session = None


def check_error_count(error_count, query_count):
    if error_count > 20 and error_count % 20 != 0:
        PS5_DISCORD_HOOK_BUG_REPORT.send(
            '<Amazon query warning!> error margin exceeded : ' + str(error_count) + ' errors\nQuery #' + str(
                query_count))


def scrapAmazon():
    test_url = 'https://www.amazon.ca/NEW-Razer-Mamba-Wireless-Capability/dp/B07GBYYSMF/ref=pd_sbs_2?pd_rd_w=ANR9f&pf_rd_p=3885b243-7797-4c4b-b0ae-97ca9ec36283&pf_rd_r=9RYV4B8NYA5EBMC9VMMX&pd_rd_r=65ef63ef-e18c-4b5a-939c-38e736964566&pd_rd_wg=IyuDn&pd_rd_i=B07GBYYSMF&psc=1'
    i = 0
    error_count = 0
    global DIGIT_AMZ_RESULT
    global DISK_AMZ_RESULT
    while True:
        try:
            # Amazon query
            session = HTMLSession()
            HTML_AMZ = session.get(PS5Urls.AMAZON_DIGITAL.value if i % 2 == 0 else PS5Urls.AMAZON_DISC.value)
            # HTML_AMZ = session.get(test_url if i % 2 == 0 else PS5Urls.AMAZON_DISC.value) # TODO for test only
            HTML_AMZ.html.render(retries=1, timeout=15)

            if i % 2 == 0:
                DIGIT_AMZ_RESULT = HTML_AMZ.html.xpath(Amazon.PATH)
            else:
                DISK_AMZ_RESULT = HTML_AMZ.html.xpath(Amazon.PATH)
            print(DIGIT_AMZ_RESULT, DISK_AMZ_RESULT)
            session.close()
            error_count = 0
            i += 1
            time.sleep(3)
        except Exception:
            error_count += 1
            check_error_count(error_count, i)
            session.close()


if __name__ == '__main__':
    # discord setup
    PS5_DISCORD_HOOK = Webhook.from_url(PS5_DISCORD_CHANNEL, adapter=RequestsWebhookAdapter())
    PS5_DISCORD_HOOK_BUG_REPORT = Webhook.from_url(PS5_DISCORD_BUG_REPORT_CHANNEL, adapter=RequestsWebhookAdapter())

    # welcomes subscribers
    PS5_DISCORD_HOOK.send(SERVER_WELCOME)

    a = BestBuy(PS5Urls.BESTBUY_DIGITAL_REQUEST, PS5Urls.BESTBUY_DISC_REQUEST)
    b = LaSource(PS5Urls.LASOURCE_DIGITAL, PS5Urls.LASOURCE_DISC)
    c = EBGames(PS5Urls.EBGAMES_DIGITAL, PS5Urls.EBGAMES_DISC)
    d = Amazon(PS5Urls.AMAZON_DIGITAL, PS5Urls.AMAZON_DISC)
    e = Walmart(PS5Urls.WAL_AMZ, PS5Urls.WAL_AMZ)

    a.start()
    b.start()
    c.start()
    d.start()
    e.start()

    # signal server is running
    PS5_DISCORD_HOOK.send(SERVER_START)
    time.sleep(3)

    # scrapAmazon()
