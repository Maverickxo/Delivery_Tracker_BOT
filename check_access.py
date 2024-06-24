from aiogram import types

alladmin_ids = [5869013585, 1444325514]


def auth(func):
    async def wrapper(message):
        if message['from']['id'] not in alladmin_ids:
            return await message.reply("Доступ запрещен", reply=False)
        return await func(message)

    return wrapper


def aut_cgt():
    def decorator(func):
        async def wrapper(message: types.Message):
            if message.chat.type != types.ChatType.PRIVATE:
                await message.reply("Пожалуйста, отправляйте сообщения боту только в приватных чатах.")
                return
            return await func(message)

        return wrapper

    return decorator
