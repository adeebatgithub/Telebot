###################################################
# Telegram Bot
# Author  : Adeebdanish
# version : 2.0
###################################################

import telebot
from telebot import types
import os, sqlite3, platform
from dotenv import load_dotenv
from datetime import datetime

from utils.dbman import DBMan
from utils import settings


class Bot(DBMan):
    db_path = "data.db"
    table_name = "Files"

    # data structure (id, name, file_id, file_uid, file_type)

    def __init__(self):

        """
        1- Forward tag remover
        2- File search
        """

        super().__init__()
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        self.bot = telebot.TeleBot(API_KEY)
        self.log("Bot started...")
        self.search_name_list = {}
        self.messages_dict = {}

        self.bot.set_update_listener(self.main)

        @self.bot.message_handler(commands=["help", "up", "about"])
        def command_handler_func(message):
            cmd_func = {
                "/help": self.help_desk,
                "/up": self.up,
                "/about": self.about,
            }
            try:
                cmd_func[message.text](message)
            except Exception as e:
                self.log(f"cmd_err : {e} : {message.text}")

        @self.bot.callback_query_handler(func=lambda call: call.data in ["ftr_btn", "done"])
        def call_handle_func(call):
            calls_dict = {
                "ftr_btn": self.ftr_btn_call_handle,
                "done": self.done_btn_call_handle,
            }
            try:
                calls_dict[call.data](call)
            except Exception as e:
                self.log(f"call_err : {e} : {call.data}")

        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "search")
        def search_call_handle_func(call):
            self.search_call_handle(call)

        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "next")
        def next_call_handle_func(call):
            self.nxt_btn_call_handle(call)

        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "back")
        def back_call_handle_func(call):
            self.back_btn_call_handle(call)

        ################################################################################################################

        # self.bot.polling()
        try:
            self.bot.polling(none_stop=True, timeout=120)
        except ConnectionError:
            self.log("error : not connected to network")
            quit()
        except Exception as e:
            self.log(f"Bot_down_err : {e}")
            self.log("restarting Bot...")
            self.__init__()

        ################################################################################################################

    def log(self, txt: str) -> None:

        print(f"[{datetime.now()}] {txt}")

    def main(self, messages):
        for message in messages:

            if message.text is not None:
                if message.text == "/start":
                    self.start(message)

                if message.forward_date is not None:
                    self.bot.send_message(
                        message.chat.id,
                        message.text,
                    )

                if "/search" in message.text:

                    if message.text == "/search":
                        self.bot.send_message(
                            message.chat.id,
                            "usage : /search <movie name>"
                        )
                    else:
                        self.search_data(message)

            if message.content_type in ["document", "video"]:
                if message.chat.id in self.messages_dict.keys():
                    self.messages_dict[message.chat.id].append(message)
                else:
                    self.messages_dict[message.chat.id] = [message]
                self.save_data(message)

        if len(self.messages_dict) != 0:
            self.tool()

    def start(self, message):
        self.log(f"{message.chat.username} started")
        self.bot.send_message(
            message.chat.id,
            settings.START_REPLAY,
        )

    def help_desk(self, message):
        self.bot.send_message(
            message.chat.id,
            settings.HELP_REPLAY,
        )

    def about(self, message):
        self.bot.send_message(
            message.chat.id,
            settings.ABOUT_REPLAY,
        )

    def up(self, message):
        self.bot.send_message(
            message.chat.id,
            "I am up",
        )

    def tool(self):

        for chat_id in self.messages_dict.keys():
            markup = types.InlineKeyboardMarkup()
            ftr_btn = types.InlineKeyboardButton(
                " Remove forward tag ",
                callback_data="ftr_btn",
            )
            dn_btn = types.InlineKeyboardButton(
                " Nothing ",
                callback_data="done",
            )
            markup.add(ftr_btn)
            markup.add(dn_btn)

            self.bot.send_message(
                chat_id,
                "What you want to do?",
                reply_markup=markup,
            )

    def send_doc(self, message):
        self.log(f"doc_rcv : {message.document.file_name}")
        self.bot.send_document(
            message.chat.id,
            message.document.file_id,
        )
        self.log(f'doc_snd : {message.document.file_name}')

    def send_vid(self, message):
        self.log(f"vid_rcv : {message.video.file_name}")
        self.bot.send_video(
            message.chat.id,
            message.video.file_id,
        )
        self.log(f'vid_snd : {message.video.file_name}')

    def save_data(self, message):
        col_data = {}
        if message.content_type == "document":
            col_data["name"] = message.document.file_name
            col_data["file_id"] = message.document.file_id
            col_data["file_uid"] = message.document.file_unique_id
        if message.content_type == "video":
            col_data["name"] = message.video.file_name
            col_data["file_id"] = message.video.file_id
            col_data["file_uid"] = message.video.file_unique_id
        col_data["file_type"] = message.content_type

        uid_col = self.db_fetch_col(col="file_uid")
        file_ids = [col[0] for col in uid_col]
        if col_data["file_uid"] not in file_ids:
            self.db_insert(col_data=col_data)
            self.log(f"dta_svd: name:{col_data['name']}")

    def search_data(self, message):
        file_name = message.text[8:].lower().split()
        self.search_name_list = {}

        files = self.db_fetch_all()
        for data in files:
            count = 0
            for name in file_name:
                if any(name in data[1].lower().split(separator) for separator in ['.', '_', ' ']):
                    count += 1
            if len(file_name) == count:
                self.search_name_list[data[1]] = data[3]
        self.display_search_data(message.chat.id, 0)

    def display_search_data(self, message_id, page):
        markup = types.InlineKeyboardMarkup()
        ln = 0
        temp_lst = []

        while ln < len(self.search_name_list):
            lst = dict(list(self.search_name_list.items())[ln:ln + 10])
            temp_lst.append(lst)
            ln += 10
        if len(self.search_name_list) != 0:
            for name, uid in temp_lst[page].items():
                btn = types.InlineKeyboardButton(
                    name,
                    callback_data=f"search#{uid}",
                )
                temp_lst.append(name)
                markup.add(btn)

        if len(self.search_name_list) > 10:
            next_btn = types.InlineKeyboardButton(
                "Next",
                callback_data=f"next#{page}",
            )

            back_btn = types.InlineKeyboardButton(
                "Back",
                callback_data=f"back#{page}",
            )
            markup.add(back_btn, next_btn, row_width=2)
        done_btn = types.InlineKeyboardButton(
            "Done",
            callback_data="done"
        )
        markup.add(done_btn)
        if len(self.search_name_list) == 0:
            txt = "MATCH NOT FOUND"
        else:
            txt = "MATCH FOUND"
        self.bot.send_message(
            message_id,
            txt,
            reply_markup=markup,
        )

    def ftr_btn_call_handle(self, call):
        self.bot.delete_message(
            call.from_user.id,
            call.message.id,
        )
        for chat_id, messages in self.messages_dict.items():
            if call.from_user.id == chat_id:
                for message in messages:
                    if message.content_type == "document":
                        self.send_doc(message)
                    if message.content_type == "video":
                        self.send_vid(message)
        self.messages_dict.__delitem__(call.from_user.id)

    def nxt_btn_call_handle(self, call):

        self.bot.delete_message(
            call.from_user.id,
            call.message.id,
        )
        page = int(call.data.split("#")[-1]) + 1
        self.display_search_data(
            call.from_user.id,
            page,
        )

    def done_btn_call_handle(self, call):

        self.messages_dict = {}
        self.bot.delete_message(
            call.from_user.id,
            call.message.id
        )

    def back_btn_call_handle(self, call):

        self.bot.delete_message(
            call.from_user.id,
            call.message.id,
        )
        page = int(call.data.split("#")[-1]) - 1
        self.display_search_data(
            call.from_user.id,
            page,
        )

    def search_call_handle(self, call):

        file = self.db_fetch_row(file_uid = call.data.split("#")[1])
        data = [data for data in file][0]
        name = data[1]
        message_id = data[2]
        message_type = data[4]

        if message_type == "document":
            self.bot.send_document(
                call.from_user.id,
                message_id,
            )
            self.log(f"srh doc_snd: {name}")
        if message_type == "video":
            self.bot.send_video(
                call.from_user.id,
                message_id,
            )
            self.log(f"srh vid_snd: {name}")


if __name__ == "__main__":
    Bot()
