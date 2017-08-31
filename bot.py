from telegram.ext import Updater, CommandHandler, RegexHandler, Job, ConversationHandler
from telegram import  ReplyKeyboardMarkup
import telegram, krakenex
import logging, time, os
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# TELEGRAM SETUP #
telegramkeyfile = open(os.getcwd() + '/telegram.ke', 'r')
telegramkey = telegramkeyfile.readline().strip()
bot = telegram.Bot(token=telegramkey)
updater = Updater(token=telegramkey)
dispatcher = updater.dispatcher
jobs = updater.job_queue
CHAT_ID = 0 # REPLACE WITH TELEGRAM CHAT ID
VALID_USERS = [] # ADD IDS OF USERS PERMITTED TO USE BOT

# KRAKEN SETUP #
kra = krakenex.API()
kra.load_key(os.getcwd() + "/kraken.ke")

# GENERAL SETUP #
req_data = {'docalcs' : 'true'}
milestones = {'BCH' : 650}
alert_diff = 25
last = (int(time.time()) - 300) * 1000000000
RANGE = range(1)

def checkvalue(bot, update):
    if update.message.from_user.id in VALID_USERS:
        progress = bot.send_message(chat_id=update.message.chat_id, text="Checking value...")

        ret = "*##### FIAT FUNDS #####*\n"
        try:
            bal = kra.query_private('Balance')
            bal1 = kra.query_private('TradeBalance', {'asset': 'ZEUR'})
        except:
            print("Error")
            bot.edit_message_text(chat_id=update.message.chat_id, message_id=progress['message_id'], text="Error retrieving balance, please try again")

        ledgers = kra.query_private('Ledgers', {'type': 'deposit'})
        total = float(bal1['result']['eb'])
        initial_invest = 0

        try:
            ret += "EUR: " + str(bal['result']['ZEUR']) + "€" + '\n'

            try:
                ret += "USD: $" + str(bal['result']['ZUSD']) + '\n'
            except:
                pass
            ret += '\n'
        except:
            ret += "No currency was found in the wallet.\n\n"

        ret += "*##### CRYPTO FUNDS #####*\n"
        for currency in bal['result']:
            bot.edit_message_text(chat_id=update.message.chat_id, message_id=progress['message_id'], text="Checking " + currency + "...")

            print("Checking " + currency + "...")
            if currency[1:] != "EUR" and currency[1:] != "USD":
                cur = currency if len(currency) == 3 else currency[1:]
                ret += cur + ": " + bal['result'][currency] + '\n'

        for ledger in ledgers['result']['ledger']:
            initial_invest += float(ledgers['result']['ledger'][ledger]['amount'])

        ret += "\nEstimated total worth: €" + str("%.2f" % total) + " ("
        percent = (max(initial_invest, float("%.2f" % total)) / min(initial_invest, float("%.2f" % total)) - 1) * 100
        if initial_invest > total: percent *= -1

        gain = str("%.2f" % (total - initial_invest))
        if gain[0] == '-':
            gain = "-€" + gain[1:]
        else:
            gain = '+€' + gain

        ret += gain + ", " + str("%.4f" % percent) + "%)"

        bot.send_message(chat_id=update.message.chat_id, text=ret, parse_mode="Markdown")
        bot.delete_message(chat_id=update.message.chat_id, message_id=progress['message_id'])
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Not permitted")

def bitcoincash(bot, update):
    print(update.message.chat_id)
    response = kra.query_public('Ticker', {'pair': 'BCHUSD'})
    bot.send_message(chat_id=update.message.chat_id, text="*Bitcoin Cash* last sold at $" + response['result']['BCHUSD']['c'][0], parse_mode="Markdown")

def ethereum(bot, update):
    response = kra.query_public('Ticker', {'pair': 'XETHZUSD'})
    bot.send_message(chat_id=update.message.chat_id, text="*Ethereum* last sold at $" + response['result']['XETHZUSD']['c'][0], parse_mode="Markdown")

def litecoin(bot, update):
    response = kra.query_public('Ticker', {'pair': 'XLTCZUSD'})
    bot.send_message(chat_id=update.message.chat_id, text="*Litecoin* last sold at $" + response['result']['XLTCZUSD']['c'][0], parse_mode="Markdown")

def pricealert(bot, job):
    global last

    bch = kra.query_public('Trades', {'pair': 'BCHUSD', 'since': last})

    last = bch['result']['last']
    for i in bch['result']['BCHUSD']:
        if int(float(i[0])) >= milestones['BCH'] + alert_diff:
            milestones['BCH'] += alert_diff
            bot.send_message(chat_id=CHAT_ID, text="""
            *##### PRICE UPDATE #####*
            Bitcoin Cash has recently risen to $""" + str(milestones['BCH']), parse_mode="Markdown")
            break
        elif int(float(i[0])) <= milestones['BCH'] - alert_diff:
            milestones['BCH'] -= alert_diff
            bot.send_message(chat_id=CHAT_ID, text="""
            *##### PRICE UPDATE #####*
            Bitcoin Cash has recently dropped to $""" + str(milestones['BCH']), parse_mode="Markdown")
            break

def change_pricealert(bot, update):
    global alert_diff
    options = [['$25', '$50', '$100']]
    bot.send_message(chat_id=update.message.chat_id, text="Please select how often you want to be updated about price changes.",
                     reply_markup=ReplyKeyboardMarkup(options, one_time_keyboard=True))
    return RANGE

def changepricealert(bot, update):
    global alert_diff
    alert_diff = int(str(update.message.text[1:]))
    bot.send_message(chat_id=update.message.chat_id, text="Alert interval updated to " + update.message.text)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=
    """Hi! Here are some commands you may find useful:
    *- /checkvalue *- find out how your cryptocurrencies are doing
    *- /bitcoincash *- find out value of bitcoin cash
    *- /litecoin *- find out value of litecoin
    *- /ethereum *- find out value of ethereum
    *- /alertinterval *- change the alert interval for bitcoin cash

    To view this help prompt again, just type /start.""", parse_mode="Markdown")

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

start_handler = CommandHandler('start', start)
val_handler = CommandHandler('checkvalue', checkvalue)
bch_handler = CommandHandler('bitcoincash', bitcoincash)
eth_handler = CommandHandler('ethereum', ethereum)
ltc_handler = CommandHandler('litecoin', litecoin)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('alertinterval', change_pricealert)],
    states={RANGE: [RegexHandler('^(\$25|\$50|\$100)$', changepricealert)]},
    fallbacks={}
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(val_handler)
dispatcher.add_handler(bch_handler)
dispatcher.add_handler(eth_handler)
dispatcher.add_handler(ltc_handler)
dispatcher.add_handler(conv_handler)
# jobs.run_repeating(pricealert, interval=60.0)

dispatcher.add_error_handler(error)

updater.start_polling()
