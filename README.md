# CryptoBot
A basic Telegram bot for communicating with a Kraken account.
Uses the Python Telegram Bot (https://github.com/python-telegram-bot/python-telegram-bot) and Krakenex (https://github.com/veox/python3-krakenex)

## Usage
- Register a new bot on Telegram by messaging @BotFather
- Enter your API keys for Kraken and Telegram into the relevant files (kraken.ke and telegram.ke)
- Update the value of CHAT\_ID to the Telegram chat ID that contains the bot 

## Commands
Some demo commands are included for specific currencies; adding new functionality to the bot is straightforward by just replacing the currency name in the code.
- /checkvalue - find out how your cryptocurrencies are doing
- /bitcoincash - find out value of bitcoin cash
- /litecoin - find out value of litecoin
- /ethereum - find out value of ethereum
- /alertinterval - change the alert interval for bitcoin cash
