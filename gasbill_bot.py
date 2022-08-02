from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from os import getenv

import chromedriver_autoinstaller
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
import telegram.ext as tgram_e


class GasBot:
    def __init__(self, key):
        self._updater = tgram_e.Updater(key, use_context=True)
        self._dispatcher = self._updater.dispatcher
        self.add_handlers(self._dispatcher)

    def run(self):
        self._updater.start_polling()
        self._updater.idle()

    def init_browser(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--headless")
        chromedriver_autoinstaller.install()
        return webdriver.Chrome(options=options)

    def add_handlers(self, dispatcher):
        dispatcher.add_handler(tgram_e.CommandHandler("start", self.start))
        dispatcher.add_handler(tgram_e.CallbackQueryHandler(self.gas_command))

    def start(self, update: Update, context: tgram_e.CallbackContext):
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

    def gas_command(self, update: Update, context: tgram_e.CallbackContext):
        callback = update.callback_query.data
        if callback == "gas_button":
            self._browser = self.init_browser()
            text = self.check_bill()
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
            )

    def check_bill(self):
        self._browser.get("https://itd-pbx.com/mgas/")

        customer_num = self._browser.find_element(By.CSS_SELECTOR, "input[type=text")
        CLIENT_NUM = getenv("MY_CLIENT_NUM")
        customer_num.send_keys(CLIENT_NUM)
        actions = ActionChains(self._browser)
        actions.send_keys(Keys.TAB * 2, Keys.ENTER).perform()
        try:
            form = self._browser.find_element(
                By.CSS_SELECTOR, "body > div > form > div:nth-child(1)"
            )
        except:
            answer = "Looks like your input was wrong.\nTry again, make sure you type numbers only.\n\n\
Oh, and are you sure you are a client of מרכז הגז?"
        else:
            answer = form.text.split("\n")[-1].strip()

        self._browser.quit()
        return answer


if __name__ == "__main__":
    load_dotenv()
    key = getenv("KEY")
    bot = GasBot(key)
    bot.run()
