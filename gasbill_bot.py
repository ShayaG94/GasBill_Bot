from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from os import getenv
import telebot

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
import telegram
import telegram.ext as tgram_e

load_dotenv()
BOT_KEY = getenv("KEY")
CLIENT_NUM = getenv("MY_CLIENT_NUM")
bot = telebot.TeleBot(BOT_KEY)

# bot.set_my_commands([telebot.types.BotCommand("/Gas", "Check Gas Bill")])


def gas_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.get("https://itd-pbx.com/mgas/")

    customer_num = browser.find_element(By.CSS_SELECTOR, "input[type=text")
    customer_num.send_keys(CLIENT_NUM)
    actions = ActionChains(browser)
    actions.send_keys(Keys.TAB * 2, Keys.ENTER).perform()

    try:
        form = browser.find_element(
            By.CSS_SELECTOR, "body > div > form > div:nth-child(1)")
    except:
        answer = "Looks like your input was wrong.\nTry again, make sure you type numbers only.\n\n\
Oh, and are you sure you are a client of מרכז הגז?"
    else:
        answer = form.text.split("\n")[-1].strip()

    browser.quit()
    return answer


@bot.message_handler(commands=['Gas'])
def check_gas_bill(message):
    # print(message.text)
    username = message.from_user.first_name
    checking_msg = f"שניה איתך {username},\nאני בודק רגע, כבר נותן תשובה..."
    bot.send_message(message.chat.id, checking_msg)

    answer = gas_driver()

    bot.send_message(message.chat.id, answer)


if __name__ == "__main__":
    bot.polling()
