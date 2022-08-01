from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from os import getenv

# import chromedriver_autoinstaller
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyMarkup,
    Update,
)
import telegram
import telegram.ext as tgram_e


def init_bot():
    BOT_KEY = getenv("KEY")
    updater = tgram_e.Updater(BOT_KEY, use_context=True)
    disp = updater.dispatcher
    add_handlers(disp)
    updater.start_polling()
    updater.idle()


def start(update: Update, context: tgram_e.CallbackContext):
    name = update.message.chat.first_name
    start_text = f"Hello {name}! Welcome to Shaya's Bot!\n\n\
    Press the button to continue:"

    INLINE_BUTTONS = [
        [InlineKeyboardButton(text="Check Gas Bill", callback_data="gas_button")]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_text,
        reply_markup=InlineKeyboardMarkup(INLINE_BUTTONS),
    )


def gas_command(update: Update, context: tgram_e.CallbackContext):
    callback = update.callback_query.data
    if callback == "gas_button":
        text = gas_driver()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
        )


def add_handlers(dispatcher):
    dispatcher.add_handler(tgram_e.CommandHandler("start", start))
    dispatcher.add_handler(tgram_e.CallbackQueryHandler(gas_command))


# Start browser func
# Get link etc.


def gas_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--headless")
    try:
        browser = webdriver.Chrome(options=options)
    except common.exceptions.SessionNotCreatedException:
        return "Something went wrong :/"
    else:
        browser.get("https://itd-pbx.com/mgas/")

    customer_num = browser.find_element(By.CSS_SELECTOR, "input[type=text")
    CLIENT_NUM = getenv("MY_CLIENT_NUM")
    customer_num.send_keys(CLIENT_NUM)
    actions = ActionChains(browser)
    actions.send_keys(Keys.TAB * 2, Keys.ENTER).perform()

    try:
        form = browser.find_element(
            By.CSS_SELECTOR, "body > div > form > div:nth-child(1)"
        )
    except:
        answer = "Looks like your input was wrong.\nTry again, make sure you type numbers only.\n\n\
Oh, and are you sure you are a client of מרכז הגז?"
    else:
        answer = form.text.split("\n")[-1].strip()

    browser.quit()
    return answer


if __name__ == "__main__":
    load_dotenv()
    init_bot()
