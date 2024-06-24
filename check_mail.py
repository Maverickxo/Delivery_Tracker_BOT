import asyncio
import sqlite3
import requests
from datetime import datetime
from write_log import log_check_tr

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


async def extract_track():
    conn, cursor = get_connection_and_cursor()
    cursor.execute("SELECT tracknum FROM tracking ORDER BY tracknum")
    track_nums = cursor.fetchall()

    def extract_time(last_operation):
        datetime_obj = datetime.strptime(last_operation, "%Y-%m-%dT%H:%M:%S.%f%z")
        time_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        return time_str

    track_handed, track_awaiting, track_progress, count = 0, 0, 0, 0

    for track_num in track_nums:
        params = {'language': 'ru', 'track-numbers': [track_num[0]]}

        response = requests.get(
            'https://www.pochta.ru/api/tracking/api/v1/trackings/by-barcodes',
            params=params,
            cookies=cookies,
            headers=headers,
        )

        data = response.json()
        if response.status_code == 200:
            if data["detailedTrackings"]:
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

                        track_progress += 1
                        count += 1
                        print(f'{count}.  {recipient}: {status} |{time}| {humanStatus} ~ {datesplit} ')

                    else:
                        track_progress += 1
                        count += 1
                        print(f'{count}.  {recipient}: {status} |{time}|  ')

                else:
                    recipient = data["detailedTrackings"][0]["trackingItem"]["recipient"]
                    barcode = data["detailedTrackings"][0]["trackingItem"]["barcode"]
                    common_status = data["detailedTrackings"][0]["trackingItem"]["commonStatus"]
                    count += 1
                    track_awaiting += 1
                    print(f'{count}.  {barcode} - {recipient}: {status} |{time}| {common_status} ')

                if status == "Получено адресатом":
                    cursor.execute("DELETE FROM tracking WHERE tracknum=?", (track_num[0],))
                    conn.commit()
                    track_handed += 1
                    print("Трек-номер", track_num[0], "удален из базы данных.")

            else:
                print("Данные для трек-номера", track_num[0], "не найдены.")
        else:
            print("Ошибка при выполнении запроса для трек-номера", track_num[0], ":", response.status_code)

    print("+----------------------")
    print(f"|Получено\удалено - {track_handed}")
    print(f"|Треков на вручение - {track_awaiting}")
    print(f"|Треков в пути - {track_progress}")
    print("+----------------------")
    log_check_tr(track_handed, track_awaiting, track_progress)
# asyncio.run(extract_track())
