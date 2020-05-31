import json
import telebot
import logging
import os

CONFIG = json.load(open('config.json'))
bot = telebot.TeleBot(CONFIG['tel_bot_token'])
user_register_step = []
logger = logging.getLogger()

logging.basicConfig(filename=CONFIG['log_file'],
                        filemode='a',
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)


def get_list_users() -> dict:
    if os.path.exists(CONFIG['users_file']):
        with open(CONFIG['users_file']) as json_file:
            return dict(json.load(json_file))
    else:
        return {}


def save_users(users: dict):
    with open(CONFIG['users_file'], 'w+', encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False)


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            logger.info(f"id:{m.chat.id},first_name:{m.chat.first_name},text:{m.text}")


bot.set_update_listener(listener)


@bot.message_handler(commands=['help'])
def command_help(m):
    help_text = "The following commands are available: \n"
    help_text += "/start \n"
    help_text += "/help \n"
    bot.send_message(m.chat.id, help_text, reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['start'])
def start(message):
    user = get_list_users().get(str(message.chat.id), None)
    if user is None:
        markup = telebot.types.ReplyKeyboardMarkup()
        contact = telebot.types.KeyboardButton('Contact', request_contact=True)
        markup.add(contact)
        user_register_step.append(message.chat.id)
        bot.send_message(message.chat.id, 'Please your contact', reply_markup=markup)
    else:
        msg = 'YOU ARE REGISTERED\n'
        msg += 'You can use :\n'
        msg += '/open_gate\n'
        bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda m: m.chat.id in user_register_step, content_types=['contact'])
def command_register_step_two(message):
    users = get_list_users()
    users[str(message.contact.user_id)] = message.contact.__dict__
    save_users(users)
    user_register_step.remove(message.chat.id)
    msg = 'Congratulations, you have registered.\n'
    msg += 'You can use :\n'
    msg += '/open_gate\n'
    bot.send_message(message.chat.id, msg, reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['open_gate'], func=lambda m: get_list_users().get(str(m.chat.id), False))
def open_gate(message):
    cid = message.chat.id
    bot.send_chat_action(cid, 'typing')
    bot.send_message(cid, 'OPEN GATE!!!!')


# Timeout in seconds for long polling.
bot.polling(timeout=20)
