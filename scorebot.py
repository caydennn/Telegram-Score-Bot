from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import logging
import json
import psycopg2

''' 
You need to modify the following variables in your own bot:

# SQL PORTION
1) DB_NAME
2) DB_USER
3) DB_PASS
4) DB_HOST
5) DB_PORT (only if its different from 5432)


# TELEGRAM PORTION
1) Passwords (To access the update score function)
2) Telegram Token (This is under the function main())

! Do NOT use this code structure in production! 
It is advisable to save your sensitive information in a env file and reference the variables from there.
'''

# Setting up logging to debug in heroku 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)


''' SQL CODE PORTION ''' 

#! SQL - Establish Connection
def get_db_connection():

    DB_NAME = "<<YOUR DB NAME FROM HEROKU>>"
    DB_USER = "<<YOUR DB USER FROM HEROKU>>"
    DB_PASS = "<<YOUR DB PASS FROM HEROKU>>"
    DB_HOST = "<<YOUR DB HOST FROM HEROKU>>"
    DB_PORT = "5432" 

    try:
        conn = psycopg2.connect(database = DB_NAME, user = DB_USER,
                        password = DB_PASS, host = DB_HOST, port = DB_PORT)

        print ('Database connected succcessfully')
        logger.info('Database connected succcessfully')
        return conn 

    except:
        print ("Database not connected")
        logger.info("Database not connected")



#! SQL - Get online scores as a dict
def get_db_scores():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT info FROM scores")

    rows = cur.fetchall()
    #* Current Data is type Dictionary
    current_data = rows[0][0]
    conn.close()

    logger.info("Data retrieved successfully")
    return current_data

#! SQL - Replaces current db dictionary with new dictionary
def update_db_scores(newdict):
    # Convert the Dict into a string
    score_str = json.dumps(newdict)

    conn = get_db_connection()
    cur = conn.cursor()
    table_name = "scores"
    sql_string = ("UPDATE {0} set INFO = '{1}' WHERE ID = 1".format(table_name, score_str ))

    cur.execute(sql_string)
    conn.commit()

    print("Data updated successfully")
    logger.info("Data updated successfully")

    print ("Total row affected " + str(cur.rowcount))
    logger.info("Total row affected " + str(cur.rowcount))

    conn.close()



''' TELEGRAM CODE PORTION ''' 

### Add the passwords you want to be able to access the updater (Feel free to delete the current passwords)
passwords = ['<<YOUR PASSWORD HERE>>', 'password', 'password1', 'password2']

VERIFYING, CHOOSINGGROUPING, ACTION, ADD, DEDUCT, ISTHEREMORE, ANYMORE = range(7)

group_keyboard = [['G1', 'G2'],
                  ['G3', 'G4'],
                  ['Done']]
group_markup = ReplyKeyboardMarkup(group_keyboard, one_time_keyboard=True)

action_keyboard = [['Add', 'Deduct'],
                    ['Cancel']]

action_markup = ReplyKeyboardMarkup(action_keyboard, one_time_keyboard=True)

more_keyboard = [['More', 'Done']]
more_markup = ReplyKeyboardMarkup(more_keyboard, one_time_keyboard=True)


# The callback function thats invoked when /start is sent
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text="Hello! Type /score to get the current scoreboard.\n(For Mods: Update scores with /updatescores) ")

def get_score(update, context):
    data = get_db_scores()

    scoreboard = """
Group 1: {G1}
Group 2: {G2}
Group 3: {G3}
Group 4: {G4}

DON'T GIVE UP!
    """.format(**data)
    context.bot.send_message(chat_id=update.effective_chat.id, text = scoreboard)


def start_update(update, context):
    update.message.reply_text("Update the different group scores here!\nType in password:\nor /cancel")
    return VERIFYING

def verify_user(update, context):
    user = update.message.from_user
    update.message.reply_text("Welcome {}".format(user.first_name))
    update.message.reply_text("Choose the group that you want to update the score of.", reply_markup = group_markup)
    return CHOOSINGGROUPING


def action(update, context):
    text = update.message.text
    context.user_data['group'] = text
    update.message.reply_text('{}: Are you adding or subtracting scores?'.format(text), reply_markup = action_markup)
    return ACTION 

def add_score(update, context):
    update.message.reply_text('How much are you adding?')
    return ADD

def adding_score(update, context):
    text = update.message.text
    group = context.user_data['group'] #G1 or G2 etc ...
    
    # Get the current scores 
    score_dict = get_db_scores()

    # Make the changes
    initialValue = int(score_dict[group])
    newValue = initialValue + int(text)
    score_dict[group] = newValue

    # Update DB with the new dictionary 
    update_db_scores(score_dict)

    update.message.reply_text('Added {} to {}'.format(text, group))
    update.message.reply_text('Send anything to continue')

    return ISTHEREMORE

def minus_score(update, context):
    update.message.reply_text('How much are you deducting?')
    return DEDUCT

def minusing_score(update, context):
    text = update.message.text
    group = context.user_data['group'] #G1 or G2 etc ...

    # Get the current scores 
    score_dict = get_db_scores()

    # Make the changes
    initialValue = int(score_dict[group])
    newValue = initialValue - int(text)
    score_dict[group] = newValue

    # Update DB with the new dictionary 
    update_db_scores(score_dict)

    update.message.reply_text('Deducted {} from {}'.format(text, group))
    update.message.reply_text('Send anything to continue')

    return ISTHEREMORE
    
def is_there_more(update, context):
    score_dict = get_db_scores()

    update.message.reply_text(score_dict)
    update.message.reply_text('Do you want to continue?', reply_markup = more_markup)
    return ANYMORE

def cancel(update, context):
    user = update.message.from_user
    # with open ('scores.json', 'w') as json_file:
    #     json.dump(score_dict, json_file)
    
    logger.info("User %s canceled the score updater.", user.first_name)
    update.message.reply_text('User canceled the score updater. Bye {}!'.format(user.first_name),
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():

    ### Add your Telegram Token in the line below provided from BotFather
    updater = Updater(token= <<YOUR_TELEGRAM_TOKEN_HERE>>, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    score_handler = CommandHandler('score', get_score)
    dispatcher.add_handler(score_handler)


    # Conversation to update scores
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('updatescores', start_update)],

        states={
            VERIFYING: [MessageHandler(Filters.text(passwords), verify_user),
                        MessageHandler(Filters.regex('^(/cancel)$'), cancel)],

            CHOOSINGGROUPING: [MessageHandler(Filters.regex('^(G1|G2|G3|G4)$'), action),
                                MessageHandler(Filters.regex('^(Done)$'), cancel)],

            ACTION: [MessageHandler(Filters.regex('^(Add)$'), add_score),
                     MessageHandler(Filters.regex('^(Deduct)$'),minus_score)],

            ADD: [MessageHandler(Filters.text, adding_score)],

            DEDUCT: [MessageHandler(Filters.text, minusing_score)],

            ISTHEREMORE: [MessageHandler(Filters.text, is_there_more)],

            ANYMORE: [MessageHandler(Filters.regex('^(More)$'), verify_user),
                    MessageHandler(Filters.regex('^(Done)$'), cancel)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


    dispatcher.add_handler(conv_handler)
    
    
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
