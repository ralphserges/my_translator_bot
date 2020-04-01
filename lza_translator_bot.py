from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os, requests, uuid, json, time
#################################### ALL ENVIRONMENT VARIABLES ####################################
key_var_name = 'TRANSLATOR_TEXT_SUBSCRIPTION_KEY'
if not key_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(key_var_name))
subscription_key = os.environ[key_var_name]

endpoint_var_name = 'TRANSLATOR_TEXT_ENDPOINT'
if not endpoint_var_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(endpoint_var_name))
endpoint = os.environ[endpoint_var_name]

bot_token_name = 'BOT_TOKEN'
if not bot_token_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(bot_token_name))
bot_token = os.environ[bot_token_name]

port_name = 'PORT'
if not port_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(port_name))
the_port = int(os.environ.get(port_name,'5000'))

heroku_name = 'HEROKU_APP_NAME'
if not heroku_name in os.environ:
    raise Exception('Please set/export the environment variable: {}'.format(heroku_name))
heroku_app_name = os.environ[heroku_name]


#################################### AVAILABLE LANGUAGE ####################################
the_language_dict = {'chinese': 'zh-Hans', 'english': 'en','japanese': 'ja','korean': 'ko', 'vietnamese': 'vi'}
avaliable_language_list = ['english','chinese','vietnamese','korean','japanese']
the_selected_list = []
the_selected_code = []

#################################### TRANSLATION ####################################
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

def get_translated_text(text, translate_to_this_langauge):
    
    params = '&to={}'.format(translate_to_this_langauge)
    constructed_url = endpoint + params

    body = [{
    'text' : text
    }]

    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    the_dict = response[0]
    the_text_dict = the_dict.get('translations')
    
    return the_text_dict[0].get('text')


def the_translator(bot,update):    
    if len(the_selected_code) != 0 :
        for language_code in the_selected_code:
            text = update.message.text
            translated_text = get_translated_text(text, language_code)
            update.message.reply_text('Translated: ' + translated_text)
    
#################################### BOTS ####################################
def start(bot, update):
    update.message.reply_text(main_menu_message(), reply_markup=main_menu_keyboard())

def main_menu(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=main_menu_message(),
                          reply_markup=main_menu_keyboard())
    
def select_language(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=select_language_message(),
                          reply_markup=select_language_keyboard())
    
def select_again_option(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=added_language_message(query.data),
                          reply_markup=select_again_option_keyboard())    
       
def show_selected_list(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=show_selected_list_message(),
                          reply_markup=show_selected_list_keyboard())

def start_conversation(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=start_conversation_message())
    
    # this is to identify the language code that user has selected for translation
    # this is to update the_selected_list and the language code list
    the_selected_list_updated = the_selected_list.copy()
    the_selected_code.clear()
    
    for key in the_language_dict.keys():
        for i in the_selected_list_updated:
            if (key.lower() == i.lower()) and the_language_dict.get(key) not in the_selected_code:
                the_selected_code.append(the_language_dict.get(key))

# include a remove from list function here
def remove_from_list(bot,update):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=remove_from_list_message(query.data),
                          reply_markup=remove_from_list_keyboard())    
    
    # remove from list here
    lang_to_delete = query.data
    language = lang_to_delete.replace('remove ', '')
    if language in the_selected_list:
        the_selected_list.remove(language)
        
#################################### KEYBOARDS ####################################
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Select Language', callback_data='m1')]]   
    
    return InlineKeyboardMarkup(keyboard)
    
def select_language_keyboard():
    keyboard = [[InlineKeyboardButton('Show selected language list', callback_data='show_list')],
                    [InlineKeyboardButton('Complete selection', callback_data='complete_list')]]
    
    for i in avaliable_language_list:
        keyboard.insert(0,[InlineKeyboardButton(i, callback_data=i)])
        
    return InlineKeyboardMarkup(keyboard)

def select_again_option_keyboard():
    keyboard = [[InlineKeyboardButton('Continue to select', callback_data='continue')],
                [InlineKeyboardButton('Show selected list', callback_data='show_list_2')],
                [InlineKeyboardButton('Selection done', callback_data='complete_list_2')]]
    
    return InlineKeyboardMarkup(keyboard)

def show_selected_list_keyboard():
    keyboard = [[InlineKeyboardButton('Back to select language menu', callback_data='m1_1')]]
    
    for lang in the_selected_list:    
        keyboard.insert(0, [InlineKeyboardButton('Remove '+lang, callback_data='remove '+lang)])
        
    return InlineKeyboardMarkup(keyboard)

# include a remove from list keyboard here
def remove_from_list_keyboard():
    keyboard = [[InlineKeyboardButton('Back to select language menu', callback_data='m1_2')]]
    return InlineKeyboardMarkup(keyboard)

#################################### MESSAGES ####################################
def main_menu_message():
    return 'Hello, Welcome to lza_translator_bot. I will be translating according to the languages you set. \n\n\
To do so, proceed to select language option and choose the languages you want.\n\n\
Type /start to add or remove language you set'

def select_language_message():
    return 'Please select the languages you want to translate to'

def instruction_message():
    return 'This is the instruction on how to use lza_translator_bot'

def added_language_message(selected_language):
    # look out for duplciates
    if selected_language in the_selected_list:
        return 'It is selected already.'
    else: 
        the_selected_list.append(selected_language)
        return 'Added {} to the translation list!'.format(selected_language)

def start_conversation_message():      
    return 'Selection Completed. You can start communicating now'

def show_selected_list_message():
    sentence = 'Here are your selected language : '
    for i in the_selected_list:
        sentence += i.upper() + ', '
        
    return sentence

# include a remove from list message here
def remove_from_list_message(language_to_remove):
    return 'You ' + language_to_remove + ' from list'
    

#################################### HANDLERS ###################################    
def main():
    updater = Updater(bot_token)
    print('bot running')
    
    # when user key /start
    updater.dispatcher.add_handler(CommandHandler('start', start))

    # when user want to choose from a list of available language
    updater.dispatcher.add_handler(CallbackQueryHandler(select_language, pattern='m1'))
    updater.dispatcher.add_handler(CallbackQueryHandler(select_language, pattern='m1_1'))
    updater.dispatcher.add_handler(CallbackQueryHandler(select_language, pattern='m1_2')) 
    
    # when user is done with selection
    updater.dispatcher.add_handler(CallbackQueryHandler(start_conversation, pattern='complete_list_2'))
    updater.dispatcher.add_handler(CallbackQueryHandler(start_conversation, pattern='complete_list'))
    
    # when user want to add on to list after selecting one language
    updater.dispatcher.add_handler(CallbackQueryHandler(select_language, pattern='continue'))
    
    # when user want to see what is on the list alr
    updater.dispatcher.add_handler(CallbackQueryHandler(show_selected_list, pattern='show_list'))
    updater.dispatcher.add_handler(CallbackQueryHandler(show_selected_list, pattern='show_list_2'))
    
    # when user wants to remove selected language from list
    for j in avaliable_language_list:
        updater.dispatcher.add_handler(CallbackQueryHandler(remove_from_list, pattern='remove '+j))
        
    # after user select one language, it will prompt user if want to select again, show list or complete selection
    for i in avaliable_language_list:
        updater.dispatcher.add_handler(CallbackQueryHandler(select_again_option, pattern=i))   
    
    # the translator
    updater.dispatcher.add_handler(MessageHandler(Filters.text, the_translator))
    
    # Bot running
    #This is webhook method
    '''
    updater.start_webhook(listen='0.0.0.0',
                          port=the_port,
                          url_path=bot_token)
    
    the_url = 'https://{0}.herokuapp.com/{1}'.format(heroku_app_name,bot_token)
    
    updater.bot.set_webhook(the_url)   
    '''
   
    #This is long polling method
    '''
    while(True):
        try:
            updater.start_polling(poll_interval=5, clean=True, bootstrap_retries=10, timeout=20)
            updater.idle()
        except TimeoutError as e:
            updater.stop()

     '''
if __name__ == '__main__':
  main()
 
