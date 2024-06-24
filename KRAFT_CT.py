import os

import requests
import asyncio
import logging
from datetime import datetime, timedelta

import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from check_access import *
from config import *
from speakbot import Database
from pars_mail import *
from check_mail import extract_track
from support import *
import barcod_gen
from check_bd_track import check_and_update_komu
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = Database('user_data.db')
DATABASE_NAME = 'tracking_data.db'

cookies = {
    'PORTAL_LANGUAGE': 'ru-RU',
    'ANALYTICS_UUID': '285078ae-ccd8-485c-8c34-13f00a982a8f',
    'GUEST_LANGUAGE_ID': 'ru_RU',
    'COOKIE_SUPPORT': 'true',
    '_ym_uid': '168746507020583211',
    '_ym_d': '1687465070',
    '_ym_isad': '1',
    '_gid': 'GA1.2.1925706459.1687465071',
    '_ymab_param': 'e17dE5WaMw4tV1S5vqBIdLRW91vHXF4gRxVb6yXkxEVcCx5M1qOrhbe3zTfd5fcWkEWlpfaUVhExrrd8mCi9g0wl0Ks',
    '_ga_M4KN6VWDWQ': 'GS1.1.1687465075.1.1.1687465187.0.0.0',
    '_ga_ZSVYDXRTRX': 'GS1.1.1687465084.1.1.1687465189.0.0.0',
    'JSESSIONID': '9E45A95A5BFF548A53D1F36756F3313E',
    'referrer': 'www.google.com',
    'ssid': '1687469385519.p4zndsjn',
    '_ga': 'GA1.1.810597824.1687465071',
    '_ym_visorc': 'b',
    '_ga_26MBKTNV85': 'GS1.1.1687469385.2.0.1687469718.0.0.0',
    '_ga_GMZSRCGNLV': 'GS1.1.1687469385.2.0.1687469718.0.0.0',
    '_ga_F1CS72SQ11': 'GS1.1.1687469718.2.0.1687469718.0.0.0',
    '_ga_54LKYVF849': 'GS1.1.1687469719.2.0.1687469719.0.0.0',
    '_ga_C5B1271HPM': 'GS1.1.1687469719.2.0.1687469719.0.0.0',
    '_ga_R538W0WL5W': 'GS1.1.1687469719.2.0.1687469719.0.0.0',
    '_ga_EX012P5J5B': 'GS1.1.1687469386.2.0.1687469719.0.0.0',
}

headers = {
    'authority': 'www.pochta.ru',
    'accept': 'application/json',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': 'PORTAL_LANGUAGE=ru-RU; ANALYTICS_UUID=285078ae-ccd8-485c-8c34-13f00a982a8f; GUEST_LANGUAGE_ID=ru_RU; COOKIE_SUPPORT=true; _ym_uid=168746507020583211; _ym_d=1687465070; _ym_isad=1; _gid=GA1.2.1925706459.1687465071; _ymab_param=e17dE5WaMw4tV1S5vqBIdLRW91vHXF4gRxVb6yXkxEVcCx5M1qOrhbe3zTfd5fcWkEWlpfaUVhExrrd8mCi9g0wl0Ks; _ga_M4KN6VWDWQ=GS1.1.1687465075.1.1.1687465187.0.0.0; _ga_ZSVYDXRTRX=GS1.1.1687465084.1.1.1687465189.0.0.0; JSESSIONID=9E45A95A5BFF548A53D1F36756F3313E; referrer=www.google.com; ssid=1687469385519.p4zndsjn; _ga=GA1.1.810597824.1687465071; _ym_visorc=b; _ga_26MBKTNV85=GS1.1.1687469385.2.0.1687469718.0.0.0; _ga_GMZSRCGNLV=GS1.1.1687469385.2.0.1687469718.0.0.0; _ga_F1CS72SQ11=GS1.1.1687469718.2.0.1687469718.0.0.0; _ga_54LKYVF849=GS1.1.1687469719.2.0.1687469719.0.0.0; _ga_C5B1271HPM=GS1.1.1687469719.2.0.1687469719.0.0.0; _ga_R538W0WL5W=GS1.1.1687469719.2.0.1687469719.0.0.0; _ga_EX012P5J5B=GS1.1.1687469386.2.0.1687469719.0.0.0',
    'referer': 'https://www.pochta.ru/tracking?barcode=80110885894666',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


def get_connection_and_cursor():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    return conn, cursor


def extract_time(last_operation):
    datetime_obj = datetime.strptime(last_operation, "%Y-%m-%dT%H:%M:%S.%f%z")
    time_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return time_str


@dp.message_handler(commands=['gettrack'])
@aut_cgt()
async def get_tracking(message):
    if len(message.text.split()) == 1:
        await message.answer("Вы не указали имя для поиска трек-номеров")

    else:
        try:
            search_name = ' '.join(message.text.split()[1:])
            name_parts = search_name.split()
            if len(name_parts) == 3:
                formatted_name = await format_name(name_parts)
            elif len(name_parts) == 2:
                formatted_name = await format_name(name_parts)
            else:
                await message.answer(INFO_TEXT)
                return
        except IndexError:

            await message.answer("Введено неполное имя.")
            return

        track_numbers = await get_track_numbers(formatted_name, message)
        for track_number in track_numbers:
            data = await get_tracking_data(track_number, message, formatted_name)

            if data:
                await process_tracking_data(data, message)
            else:
                print("Данные для трек-номера", track_number, "не найдены.")


async def get_track_numbers(formatted_name, message):
    conn, cursor = get_connection_and_cursor()
    cursor.execute("SELECT tracknum, date FROM tracking WHERE komu=?", (formatted_name,))
    results = cursor.fetchall()

    if len(results) == 0:
        response_message = "Трек-номер для:  *" + formatted_name + "*  -  не найден. - /help"
        await message.answer(response_message, parse_mode='markdown')
    track_numbers = {result[0] for result in results}
    cursor.close()
    conn.close()
    return track_numbers


async def format_name(name_parts):
    name_parts = [part.replace('ё', 'е') for part in name_parts]
    formatted_name = name_parts[0].capitalize()
    if len(name_parts) > 1:
        formatted_name += " " + name_parts[1][0].capitalize() + "."
    if len(name_parts) > 2:
        formatted_name += " " + name_parts[2][0].capitalize() + "."
    return formatted_name


async def get_tracking_data(track_number, message, formatted_name):
    await message.answer('Подождите... Выполняется поиск данных для *{}*'.format(formatted_name), parse_mode='markdown')
    await asyncio.sleep(2)

    params = {'language': 'ru', 'track-numbers': track_number}
    response = requests.get(
        'https://www.pochta.ru/api/tracking/api/v1/trackings/by-barcodes',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    if response.status_code == 200:
        return response.json()
    else:
        print("Ошибка при выполнении запроса для трек-номера", formatted_name, ":", response.status_code)
        return None


async def process_tracking_data(data, message):
    last_operation = data["detailedTrackings"][0]["trackingItem"]["trackingHistoryItemList"][0]["date"]
    time = extract_time(last_operation)

    status = data["detailedTrackings"][0]["trackingItem"]["trackingHistoryItemList"][0]["humanStatus"]

    if status in ["Покинуло сортировочный центр", "Сортировка", "Прибыло в сортировочный центр",
                  "Упрощенный предоплаченный", "Покинуло место приема"]:
        recipient = data["detailedTrackings"][0]["trackingItem"]["recipient"]
        humanStatus = data["detailedTrackings"][0]["trackingItem"]["futurePathList"][1]["humanStatus"]
        date = data["detailedTrackings"][0]["trackingItem"]["futurePathList"][1]["date"]

        if date is not None:
            date = data["detailedTrackings"][0]["trackingItem"]["futurePathList"][1]["date"]
            datesplit = date.split("T")[0]

            print(f'{recipient}:\n{status} |{time}| {humanStatus} ~ {datesplit} ')
            await message.answer(f'*{recipient}:*\n{status} |{time}|\n{humanStatus} ~ |{datesplit}|',
                                 parse_mode='markdown')
        else:
            print(f'{recipient}:\n{status} |{time}|  ')
            await message.answer(f'*{recipient}:*\n{status}|{time}|', parse_mode='markdown')
    else:
        recipient = data["detailedTrackings"][0]["trackingItem"]["recipient"]
        barcode = data["detailedTrackings"][0]["trackingItem"]["barcode"]
        common_status = data["detailedTrackings"][0]["trackingItem"]["commonStatus"]

        print(f'{barcode} - {recipient}:\n{status} |{time}| {common_status}')
        barcode_filename = f'{barcode}.itf.png'
        await barcod_gen.generate_barcode(barcode, barcode_type='itf', dpi=300, module_width=0.2)

        await message.answer_photo(
            photo=open(barcode_filename, 'rb'),
            caption=f'*{recipient}:\n{barcode}*\n{status} |{time}|\n\n❗️*{common_status}*❗️',
            parse_mode='markdown'
        )

        os.remove(barcode_filename)
        await delete_track_number(data, message)

    if status == "Получено адресатом":
        await delete_track_number(data, message)


async def delete_track_number(data, message):
    track_number = data["detailedTrackings"][0]["trackingItem"]["barcode"]
    conn, cursor = get_connection_and_cursor()
    cursor.execute("DELETE FROM tracking WHERE tracknum=?", (track_number,))
    conn.commit()
    cursor.close()
    conn.close()
    await message.answer("⚠️Трек-номер удален⚠️", parse_mode='markdown')
    print("Трек-номер", track_number, "удален из базы данных.")


@dp.message_handler(commands=['alltrack'])
@auth
async def get_all_tracking(message):
    conn, cursor = get_connection_and_cursor()
    cursor.execute("SELECT COUNT(*) FROM tracking")
    count = cursor.fetchone()[0]
    conn.close()
    await message.answer(f"Треков в базе: *{count}*", parse_mode='markdown')


@dp.message_handler(commands=['start'])
@aut_cgt()
async def welcome(message: types.Message):
    await message.answer(WELCOME_INFO, parse_mode='markdown')
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)


@dp.message_handler(commands=['help'])
@aut_cgt()
async def help_info(message):
    await message.answer(HELP_TEXT, parse_mode='markdown')


@dp.message_handler(commands=['speak'])
@auth
async def speak(message: types.Message):
    users = db.get_users()
    message_count = 0
    for row in users:
        try:
            await bot.send_message(row[0], text=message.text[message.text.find(" "):])
            message_count += 1
            if int(row[1]) != 0:
                db.set_block(row[0], 0)
        except aiogram.utils.exceptions.BotBlocked:
            db.set_block(row[0], 1)
        except aiogram.utils.exceptions.ChatNotFound:
            db.delete_user(row[0])
        except aiogram.utils.exceptions.UserDeactivated:
            db.delete_user(row[0])
    await message.answer(f"Рассылка окончена.\nОтправлено сообщений: {message_count}")


@dp.message_handler(commands=['log'])
@auth
async def read_log(message: types.Message):
    with open('check_track.log', 'r', encoding='utf-8') as f2:
        check_track_content = f2.read()

    with open('add_track.log', 'r', encoding='utf-8') as f1:
        add_track_lines = f1.readlines()
        add_track_content = ''.join(add_track_lines[:60])
        remaining_add_track_content = ''.join(add_track_lines[60:])

    await message.answer(f"Треки проверены:\n`{check_track_content}`\n\n"
                         f"Дата обнновления:\n{add_track_content}",
                         parse_mode='markdown')

    if remaining_add_track_content:
        await message.answer(f"{remaining_add_track_content}", parse_mode='markdown')


@dp.message_handler(commands=['update'])
@auth
async def update_data(message: types.Message):
    current_dt = datetime.now()
    new_dt = current_dt + timedelta(hours=4)
    dt_str = new_dt.strftime("%d.%m.%Y %H:%M:%S")
    id_message = await message.answer('Загрузка данных... ' + dt_str)
    track_added, track_exists = await data_pars()
    await id_message.delete()
    check_and_update_komu()
    await message.answer(
        f"Данные загружены  {dt_str}\n|Добавлено тереков - {track_added}\n|Одинаковых тереков - {track_exists}")


@dp.message_handler(commands=['question'])
@aut_cgt()
async def ques_send(message: types.Message):
    await send_qwests(message)


@dp.message_handler(commands=['response_trackBot'])
async def res_qu(message: types.Message):
    await send_response(message)


async def auto_load_track():
    current_dt = datetime.now()
    new_dt = current_dt + timedelta(hours=4)
    dt_str = new_dt.strftime('%Y-%m-%d %H:%M:%S')
    print('Загрузка данных...', dt_str)
    await data_pars()
    print('Данные загружены\n\nПроверка базы', dt_str)
    await extract_track()
    print('Проверка окончена', dt_str)


@dp.message_handler(commands=['userct'])
@auth
async def usr_count(message: types.Message):
    usercount = db.user_count()
    await message.answer(f'Подписчиков в боте: {usercount}', parse_mode='markdown')


@dp.message_handler(commands=['adm_help'])
@auth
async def adm_mem(message: types.Message):
    await message.answer(MEMORY_ADM, parse_mode='markdown')


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_load_track, 'interval', minutes=TIMER_TASKS)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
    asyncio.get_event_loop().run_forever()
