import asyncio
import time
from datetime import datetime
from threading import Thread

from pyppeteer.errors import NetworkError
from pytz import timezone
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
from pyppeteer.errors import TimeoutError

from discord import Webhook, RequestsWebhookAdapter, Message


def lookup():
    url = 'https://www.amazon.ca/dp/B089GSVLPY/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B089GSVLPY&pd_rd_w=gxK3K&pf_rd_p=970b3512-1bd2-4757-829e-ab114c5ecd76&pd_rd_wg=0q8nc&pf_rd_r=MX7ZQKR3A72BBSHA7R4K&pd_rd_r=d7c9e3d7-b060-437d-ad74-75cbebe477b9&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyUlhYNEVaSU1YOEI2JmVuY3J5cHRlZElkPUEwNzAzNzQ4M0FQOExPV0lZUjg1VSZlbmNyeXB0ZWRBZElkPUEwNjY0MzQ2NUtFQlpFRDFPUzVDJndpZGdldE5hbWU9c3BfZGV0YWlsJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ=='
    url2 = 'https://www.amazon.ca/Razer-DeathAdder-Wireless-Gaming-Mouse/dp/B08FQMBKQG?ref_=Oct_s9_apbd_onr_hd_bw_b1LRlw3&pf_rd_r=MF59SX6Z89MD8V833K6G&pf_rd_p=5d333356-1349-535e-8f48-5ce3661b66c8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE&pf_rd_i=1233055011'
    i = 1
    while True:
        try:
            print('try ', i)
            session = HTMLSession()
            r = session.get(url if i % 2 == 0 else url2)

            r.html.render(retries=1, timeout=15)

            s = r.html.xpath('//*[@id="availability"]/span/text()[1]')
            aff = 'url :' + str(s) if i % 2 == 0 else 'url2 :' + str(s)
            print(aff)
            print('closure starting')
            session.close()
            i += 1
            time.sleep(2)
            print('closed')
        except TimeoutError:
            session.close()
            print('timeout err')
        except NetworkError:
            print('network err')
            session.close()
        except Exception as e:
            print('unknown err')
            print(e)
            session.close()


def lookup1():
    url = 'https://www.amazon.ca/dp/B089GSVLPY/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B089GSVLPY&pd_rd_w=gxK3K&pf_rd_p=970b3512-1bd2-4757-829e-ab114c5ecd76&pd_rd_wg=0q8nc&pf_rd_r=MX7ZQKR3A72BBSHA7R4K&pd_rd_r=d7c9e3d7-b060-437d-ad74-75cbebe477b9&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyUlhYNEVaSU1YOEI2JmVuY3J5cHRlZElkPUEwNzAzNzQ4M0FQOExPV0lZUjg1VSZlbmNyeXB0ZWRBZElkPUEwNjY0MzQ2NUtFQlpFRDFPUzVDJndpZGdldE5hbWU9c3BfZGV0YWlsJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ=='
    url2 = 'https://www.amazon.ca/Razer-DeathAdder-Wireless-Gaming-Mouse/dp/B08FQMBKQG?ref_=Oct_s9_apbd_onr_hd_bw_b1LRlw3&pf_rd_r=MF59SX6Z89MD8V833K6G&pf_rd_p=5d333356-1349-535e-8f48-5ce3661b66c8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE&pf_rd_i=1233055011'
    url3 = 'https://www.google.ca/'
    i = 0

    print('try ', i)
    session = HTMLSession()
    r = session.get(url)

    while i < 2:
        r.html.render(retries=1, timeout=15)

        s = r.html.xpath('//*[@id="availability"]/span/text()[1]')
        # aff = 'url :' + str(s)
        # print(aff)
        print(s)
        # r = session.get(url)
        i += 1
        time.sleep(2)


if __name__ == '__main__':
    lookup1()
    # s = str(datetime.now(tz=timezone('EST')).strftime(
    #     '%Y-%m-%d %H:%M:%S'))
    # print(s.__contains__('2020-12-30'))
# if __name__ == '__main__':
#     url = 'https://www.walmart.ca/en/ip/marvels-spider-man-miles-morales-launch-edition-playstation-5/6000202202938?rrid=richrelevance'
#     url1 = 'https://www.walmart.ca/en/ip/playstation5-console/6000202198562'
#     # url = 'https://www.amazon.ca/Gaming-VG289Q-Monitor-FreeSync-DisplayPort/dp/B0845NXCXF/ref=sr_1_1?dchild=1&keywords=VG289Q&qid=1607555324&s=videogames&sr=1-1-catcorr'
#     # url = 'https://www.amazon.ca/dp/B089GSVLPY/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B089GSVLPY&pd_rd_w=gxK3K&pf_rd_p=970b3512-1bd2-4757-829e-ab114c5ecd76&pd_rd_wg=0q8nc&pf_rd_r=MX7ZQKR3A72BBSHA7R4K&pd_rd_r=d7c9e3d7-b060-437d-ad74-75cbebe477b9&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyUlhYNEVaSU1YOEI2JmVuY3J5cHRlZElkPUEwNzAzNzQ4M0FQOExPV0lZUjg1VSZlbmNyeXB0ZWRBZElkPUEwNjY0MzQ2NUtFQlpFRDFPUzVDJndpZGdldE5hbWU9c3BfZGV0YWlsJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ=='
#     # url1 = 'https://www.amazon.ca/Razer-DeathAdder-Wireless-Gaming-Mouse/dp/B08FQMBKQG?ref_=Oct_s9_apbd_onr_hd_bw_b1LRlw3&pf_rd_r=MF59SX6Z89MD8V833K6G&pf_rd_p=5d333356-1349-535e-8f48-5ce3661b66c8&pf_rd_s=merchandised-search-11&pf_rd_t=BROWSE&pf_rd_i=1233055011'
#     # url = 'https://www.thesource.ca/en-ca/computers-tablets/printers%2c-scanners%2c-ink/all-printers/canon-pixma-g7020-megatank-wireless-all-in-one-inkjet-printer---black/p/108086845'
#     # url = 'https://www.ebgames.ca/PS5/Games/877523'
#     # url = 'https://www.ebgames.ca/Xbox%20One/Games/768992'
#     #
#     session = HTMLSession()
#     r = session.get(url)
#     r.html.render()
#     s = r.html.xpath(
#         '/html/body/div[1]/div/div[4]/div/div/div[1]/div[3]/div[2]/div/div[1]/div/div[3]/div/div/div[3]/a/p/text()[1]')
#     print(s)
