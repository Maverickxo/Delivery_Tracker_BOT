from KRAFT_CT import bot
from aiogram import types

user_id = ''
support_chat_id = '-1001823149929'


async def send_qwests(message: types.Message):
    if message.text == '/question':
        await message.answer('Введите `/question ваш вопрос` ', parse_mode='markdown')
    else:
        question_users = message.text.split('/question ', 1)[1]
        user_id = message.from_user.id
        response = f"Для ответа скопируйте `/response_trackBot {user_id} `ваш ответ"
        await bot.send_message(support_chat_id, '*Вопрос:*\n\n' + question_users + '\n\n' + response,
                               parse_mode='markdown')

        if message.chat.type == 'private':
            sender_chat_id = message.chat.id
            reply_to_message_id = message.message_id

            reply_text = f"Ваше сообщение было отправлено в чат поддержки ожидайте "
            await bot.send_message(sender_chat_id, reply_text, reply_to_message_id=reply_to_message_id)

        return user_id


async def send_response(message: types.Message):
    if len(message.text.split()) <= 2:
        await message.answer('Забыл ввести ответ ')
    else:
        command, user_id, response_text = message.text.split(' ', 2)
    try:
        await bot.send_message(chat_id=user_id, text=f'*Ответ от тех. поддержки:*\n\n {response_text}',
                               parse_mode='markdown')
        await message.answer('Ответ отправлен')
    except:
        await message.answer('Ответ не отправлен')
