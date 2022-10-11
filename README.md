# DiscordPS5Bot

**Simple and Basic bot**
This script was made to check the stock of the PS5 console on some retailers websites.                  
This works only for Canadian retailers                                                                 
Number of retailers : 5                                                                                 
Retailers supported as of now : 
- TheSource
- BestBuy Canada
- Amazon Canada
- Walmart Canada
- EB Games 

# Behavior
check every set amount of time the availability of the stock in the supported retailers website.
When some stock is found, the user is notified through a Discord Webhook (webhook link needs to be changed in the code to use your own webhook, current one in the code was for my discord server). the message sent through the webhook contains The link to the product page and if possible the quantity of the available stock.

Libraries Used
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [requests_html](https://pypi.org/project/requests-html/)
- [discord](https://pypi.org/project/discord.py/)


## *Server Shut Down 08/2021*
only code source remains
