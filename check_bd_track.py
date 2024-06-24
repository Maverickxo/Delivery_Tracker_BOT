import json
import sqlite3


def check_and_update_komu():
    conn = sqlite3.connect('tracking_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tracking WHERE (komu IS NULL OR komu = '') AND tracknum IS NOT NULL")

    records_to_update = c.fetchall()
    for record in records_to_update:
        tracknum = record[2]
        print(tracknum)
        with open('output.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for tracking_info in data["trackingsDto"]["trackings"]:
                if tracking_info["trackingItem"]["barcode"] == tracknum:
                    recipient = tracking_info["trackingItem"]["recipient"]
                    c.execute("UPDATE tracking SET komu = ? WHERE tracknum = ?", (recipient, tracknum))
                    conn.commit()
                    break
    conn.close()


check_and_update_komu()
