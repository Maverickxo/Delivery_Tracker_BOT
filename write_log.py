from datetime import datetime, timedelta
import os

log_ad_tr = 'add_track.log'
log_ck_tr = 'check_track.log'


def get_dt():
    current_dt = datetime.now()
    new_dt = current_dt + timedelta(hours=4)
    format_dt = new_dt.strftime("%d-%m-%Y %H:%M:%S")
    return format_dt


def log_added_track(track_added, track_exists, added_tract):
    format_dt = get_dt()
    if os.path.exists(log_ad_tr):
        os.remove(log_ad_tr)
        print(f"Удален файл {log_ad_tr}")
    else:
        print(f"Файл {log_ad_tr} не был удален")
    with open(log_ad_tr, 'w', encoding='utf-8-sig') as f:
        f.write(f"{format_dt}\n\n"
                f"Добавлено тереков: {str(track_added)}\n"
                f"Одинаковых тереков: {str(track_exists)}\n\n"
                f"Список:\n{''.join(added_tract)}")
    added_tract.clear()


def log_check_tr(track_handed, track_awaiting, track_progress):
    format_dt = get_dt()
    if os.path.exists(log_ck_tr):
        os.remove(log_ck_tr)
        print(f'Удален файл {log_ck_tr}')
    else:
        print(f"Файл {log_ck_tr} не удален")
    with open(log_ck_tr, 'w', encoding='utf-8-sig') as f:
        f.write(f"{format_dt}\n\n"
                f"Получено\удалено - {str(track_handed)}\n"
                f"Треков на вручение - {str(track_awaiting)}\n"
                f"Треков в пути - {str(track_progress)}\n")
