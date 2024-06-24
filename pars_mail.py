import time
import json
import sqlite3
from datetime import date


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from auth_data import *
import time
from selenium.webdriver.common.keys import Keys

from tqdm import tqdm

from auth_data import *
from write_log import log_added_track


driver_path = 'C:\chromedriver'

service = Service(driver_path)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36")

added_tract = []

async def data_pars():
    driver = webdriver.Chrome(service=service,options=chrome_options)
    track_added = 0
    track_exists = 0

    with tqdm(total=100, desc='Вход в систему') as pbar:
        driver.get("https://www.pochta.ru/api/auth/login")
        pbar.update(25)
        select_usermane = driver.find_element(By.NAME, 'username')
        select_usermane.clear()
        select_usermane.send_keys(PHONE)
        pbar.update(25)
        time.sleep(1)
        select_password = driver.find_element(By.NAME, 'userpassword')
        select_password.clear()
        select_password.send_keys(PASSWORD)
        pbar.update(25)
        select_password.send_keys(Keys.ENTER)
        pbar.update(25)

    with tqdm(total=100, desc='Получение данных') as pbar:
        driver.get("https://www.pochta.ru/api/tracking/api/v1/trackings/by-barcodes?language=ru")
        pbar.update(25)
        page_source = driver.page_source
        pbar.update(25)
        start_index = page_source.find('<pre style="word-wrap: break-word; white-space: pre-wrap;">') + len(
            '<pre style="word-wrap: break-word; white-space: pre-wrap;">')
        end_index = page_source.rfind('</pre></body></html>')
        content = page_source[start_index:end_index]
        pbar.update(25)
        with open('output.json', 'w', encoding='utf-8') as f:
            f.write(content)
            time.sleep(1)
            pbar.update(25)

    with tqdm(total=100, desc='Обработка данных') as pbar:
        with open('output.json', 'r', encoding='utf-8') as f:
            pbar.update(20)
            data = json.load(f)
            pbar.update(50)
            time.sleep(1)
            pbar.update(30)

    with tqdm(total=100, desc='Загрузка') as pbar:
        trackings = data["trackingsDto"]["trackings"]
        num_indexes = len(trackings)
        count = 0
        listnum = 0
        track_added = 0
        track_exists = 0
        for i in range(num_indexes):
            globalStatus = data["trackingsDto"]["trackings"][count]["trackingItem"]["globalStatus"]

            if globalStatus in ["IN_PROGRESS", "ARRIVED", "RETURNED"]:

                barcode = data["trackingsDto"]["trackings"][count]["trackingItem"]["barcode"]
                recipient = data["trackingsDto"]["trackings"][count]["trackingItem"]["recipient"]
                globalStatus = data["trackingsDto"]["trackings"][count]["trackingItem"]["globalStatus"]

                conn = sqlite3.connect('tracking_data.db')
                c = conn.cursor()
                c.execute(
                    '''CREATE TABLE IF NOT EXISTS tracking (id INTEGER PRIMARY KEY AUTOINCREMENT, komu TEXT, tracknum TEXT, date DATE , globalStatus TEXT)''')

                c.execute("SELECT * FROM tracking WHERE (tracknum=? OR tracknum IS NULL) AND (komu=? OR komu IS NULL)",
                          (barcode, recipient,))
                existing_record = c.fetchone()

                if existing_record is not None:
                    track_exists += 1
                    recordstatus = "|Трек существует|"

                else:
                    c.execute("INSERT INTO tracking (komu, tracknum, date, globalStatus) VALUES (?, ?, ?, ?)",
                              (recipient, barcode, date.today(), globalStatus))
                    track_added += 1
                    recordstatus = "|Данные добавлены|"
                    conn.commit()
                conn.close()
                listnum += 1
                print(f'{listnum}. {barcode} {recipient} {recordstatus} - {globalStatus} ')
                line_exist = f'{listnum}. `{barcode} {recipient}` {recordstatus} ' #TODO: parse_mode
                added_tract.append(line_exist+'\n')
            count += 1
        print("+---------------------")
        print(f"|Добавлено тереков - {track_added}")
        print(f"|Одинаковых тереков - {track_exists}")
        print("+---------------------")
        log_added_track(track_added, track_exists, added_tract)

    driver.quit()
    return track_added, track_exists
