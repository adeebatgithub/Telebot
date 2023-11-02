###################################################
# Telegram Bot
# Author  : Adeebdanish
# version : 2.0
###################################################

import telebot
from telebot import types
import os, pyfiglet, sqlite3, platform
from dotenv import load_dotenv


class Bot:

    def __init__(self):
        
        """
        1- Forward tag remover
        2- File search
        3- Instagram video download
        
        """

        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        self.bot = telebot.TeleBot(API_KEY)
        print("")
        print('\033[0;32mBot started...\033[0m')
        print('\n')
        self.path = self.get_db_path()
        self.db_data = sqlite3.connect(self.path, check_same_thread=False)
        self.db_read = self.db_data.cursor()
        self.db_write = self.db_data.cursor()
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
                print(f"\033[0;31m>> cmd_err : {e} : {message.text}\033[0m")

        @self.bot.callback_query_handler(func=lambda call: call.data in ["ftr_btn", "done"])
        def call_handle_func(call):
            calls_dict = {
                "ftr_btn": self.ftr_btn_call_handle,
                "done": self.done_btn_call_handle,
            }
            try:
                calls_dict[call.data](call)
            except Exception as e:
                print(f"\033[0;31m>> call_err : {e} : {call.data}\033[0m")


        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "search")
        def search_call_handle_func(call):
            self.search_call_handle(call)
            
        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "next")
        def next_call_handle_func(call):
            self.nxt_btn_call_handle(call)
            
        @self.bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "back")
        def back_call_handle_func(call):
            self.back_btn_call_handle(call)

###################################################

        self.bot.polling()
        #try:
        #    self.bot.polling(none_stop=True, timeout=120)
        #except ConnectionError:
       #     print("\033[0;31m>> error : not connected to network\033[0m")
        #    quit()
      #  except Exception as e:
      #      print(f"\033[0;031m>> Bot_down_err : {e}\033[0m")
      #      self.db_read.close()
        #    self.db_write.close()
         #   self.db_data.close()
        #    self.__init__()

###################################################

    def main(self, messages):
        for message in messages:
        
            if message.text != None:
                if message.text == "/start":
                    self.start(message)
                    
                if message.forward_date is not None:
                    self.bot.send_message(
                        message.chat.id,
                        message.text,
                    )
                    
                if "https://www.instagram.com/reel/" in message.text:
                    reel_id = message.text.split("reel/")[1]
                    text = "https://www.ddinstagram.com/reel/"+reel_id
                    self.bot.send_message(
                        message.chat.id,
                        text,
                    )
                
                if "/search" in message.text:
                
                    if message.text == "/search":
                        self.bot.send_message(
                            message.chat.id,
                            "usage : /search <movie name>"
                        )
                    else:
                        self.search_data(message)

            if message.content_type in  ["document", "video"]:
                if message.chat.id in self.messages_dict.keys():
                    self.messages_dict[message.chat.id].append(message)
                else:
                    self.messages_dict[message.chat.id] = [message]
                self.save_data(message)

        if len(self.messages_dict) != 0:
            self.tool()

    def start(self, message):
        
        txt = f'''
Hai,
Welcome to my territory Mr.{message.chat.first_name}.

first of all my name is KURUKKAN and i am a BOT.
currently i have only one duty, to remove forward tag from files,
maybe in the future i may have more than one duty.

Now let's look at which commands i can understand.
first one and most important one is "/help" command
in there you can find commands and what they do.

coming to my duty,
i'll tell you how to remove the forward tag of a media file.
step-1 : forward a media file to me.
step-2 : select Remove forward tag from the options
And i'll send you the file without forward tag.

Hope i'm useful for you, Enjoy my service.           
'''
        print(f">> {message.chat.username} started")
        self.bot.send_message(
            message.chat.id,
            txt,
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

    def help_desk(self, message):

        text = f'''
List of commands:

 /help    : Open command list
 /search  : (beta)search for media files
 /about   : about the Bot
        '''

        self.bot.send_message(
            message.chat.id,
            text,
        )

    def about(self, message):
        self.bot.send_message(
            message.chat.id,
            f'''
Name      : KURUKKAN
Version   : 2.0
Owner     : Adeebdanish
'''
        )

    def up(self, message):
        self.bot.send_message(
            message.chat.id,
            "I am up")

    def send_doc(self, message):
        print(f">> doc_rcv : {message.document.file_name}")
        self.bot.send_document(
            message.chat.id,
            message.document.file_id,
        )
        print(f'ftr>> doc_snd : {message.document.file_name}')

    def send_vid(self, message):
        print(f">> vid_rcv : {message.video.file_name}")
        self.bot.send_video(
            message.chat.id,
            message.video.file_id,
        )
        print(f'ftr>> vid_snd : {message.video.file_name}')

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

    def get_db_path(self):
        if platform.system() == 'Windows':
            path = "data.db"
        if platform.system() == "Linux":
            path = "/sdcard/python/bot/data.db"
        return path

    def save_data(self, message):
        if message.content_type == "document":
            name = message.document.file_name
            _id = message.document.file_id
            uid = message.document.file_unique_id
        if message.content_type == "video":
            name = message.video.file_name
            _id = message.video.file_id
            uid = message.video.file_unique_id
        _type = message.content_type

        uid_col = self.db_read.execute('''
            SELECT uid FROM Files;
        ''')
        file_ids = [col[0] for col in uid_col]
        if uid not in file_ids:
            self.db_write.execute('''
                INSERT INTO Files VALUES (?,?,?,?);
            ''', (name, _id, uid, _type))
            self.db_data.commit()
            print(f">> dta_svd : [name:{name},id:{_id},uid:{uid},type:{_type}]")

    def search_data(self, message):
        file_name = message.text[8:].lower().split()
        self.search_name_list = {}

        files = self.db_read.execute('''
            SELECT * FROM Files;
        ''')
        for data in files:
            count = 0
            for name in file_name:
                if name in data[0].lower().split(".") or name in data[0].lower().split("_") or name in data[0].lower().split(" "):
                    count += 1
            if len(file_name) == count:
                self.search_name_list[data[0]] = data[2]
        self.display_search_data(message.chat.id, 0)

    def display_search_data(self, message_id, page):
        markup = types.InlineKeyboardMarkup()
        ln = 0
        temp_lst = []
        
        while ln < len(self.search_name_list):
            
            lst = dict(list(self.search_name_list.items())[ln:ln+10])
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

    def nxt_btn_call_handle(self, call):
        self.bot.delete_message(
            call.from_user.id,
            call.message.id,
        )
        page = int(call.data.split("#")[-1])+1
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
        page = int(call.data.split("#")[-1])-1
        self.display_search_data(
            call.from_user.id,
            page,
        )

    def search_call_handle(self, call):
        file = self.db_read.execute('''
            SELECT * FROM Files WHERE uid=?;
        ''', (call.data.split("#")[1],))
        data = [data for data in file][0]
        name = data[0]
        message_id = data[1]
        message_type = data[3]

        if message_type == "document":
            self.bot.send_document(
                call.from_user.id,
                message_id,
            )
            print(f"srh>> doc_snd : {name}")
        if message_type == "video":
            self.bot.send_video(
                call.from_user.id,
                message_id,
            )
            print(f"srh>> vid_snd : {name}")

if __name__ == "__main__":
    if platform.system() == "Windows":
        os.system("cls")
    if platform.system() == "Linux":
        os.system('clear')
    print("\033[0;33m=\033[0m" * 56)
    print("\033[0;33m=\033[0m" * 56)
    print(f"\033[1;32m{pyfiglet.figlet_format('                  BOT')}\033[0m")
    print("\033[0;33m=\033[0m" * 56)
    print("\033[0;33m=\033[0m" * 56)
    print("")
    Bot()
