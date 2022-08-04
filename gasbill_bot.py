import logging
import chromedriver_autoinstaller

from os import getenv
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import telegram.ext as tgram_e
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)


class GasBot:
    def __init__(self, key):
        self._updater = tgram_e.Updater(key, use_context=True)
        self._dispatcher = self._updater.dispatcher
        self.add_handlers(self._dispatcher)
        self.setup_logger()

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
        self._user = update.message.chat
        self._log_message = f"{self._user.id} {self._user.full_name}"
        self._logger.info(self._log_message)
        start_text = f"Hello {self._user.first_name}! Welcome to Shaya's Bot!\n\n\
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
        self._logger.info(self._log_message)
        callback = update.callback_query.data
        if callback == "gas_button":
            if self._user.id != int(getenv("MY_USER_ID")):
                wait_text = "אני לא באמת מכיר אותך, אז אין לי מושג אם יש לך חשבון גז.\n\n\
ביוש\n\n\
סתם, it's a working progress, כמו שאומרים... נתראה בעתיד"
                self.send_message(update, context, wait_text)
            else:
                wait_text = "וואי וואי כמה דרישות... חכה רגע"
                self.send_message(update, context, wait_text)
                self._browser = self.init_browser()
                client_num = getenv("MY_CLIENT_NUM")
                bill_answer = self.check_bill(client_num)
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=bill_answer,
                )

    def check_bill(self, client_num):
        self._browser.get("https://itd-pbx.com/mgas/")

        customer_num = self._browser.find_element(By.CSS_SELECTOR, "input[type=text")
        customer_num.send_keys(client_num)
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

    def send_message(self, update: Update, context: tgram_e.CallbackContext, text: str):
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def setup_logger(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level=logging.DEBUG)
        fh = logging.FileHandler("gasbot.log")
        formatter = logging.Formatter("%(asctime)s %(message)s: %(funcName)s")
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)


def main():
    load_dotenv()
    key = getenv("KEY")
    bot = GasBot(key)
    bot.run()


if __name__ == "__main__":
    main()
