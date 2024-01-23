
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

####################################################
# Database settings 
####################################################

DB_ENGINE = "psql"
DB_CONFIG = {
    
    "NAME":os.getenv("DB_NAME"),
    "HOST":os.getenv("DB_HOST"),
    "PORT":os.getenv("DB_PORT"),
    "USER":os.getenv("DB_USER"),
    "PASSWORD":os.getenv("DB_PASSWORD"),
}
TABLE_NAME = "Files"

####################################################
# Replay messages
####################################################

START_REPLAY = '''
Hai,
Welcome to my territory Mr.{}

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

HELP_REPLAY = '''
List of commands:

 /help    : Open command list
 /search  : (beta)search for media files
 /about   : about the Bot
'''

ABOUT_REPLAY = '''
Name      : KURUKKAN
'''
