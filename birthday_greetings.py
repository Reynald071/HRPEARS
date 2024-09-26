import time

import requests
import schedule


def job():
    r = requests.get('https://caraga-portal.dswd.gov.ph/sms/notification/birthday-greetings/QRDHafgx6fsWb3cav9MEdD5Gvb6rayeJ')
    print(r)


schedule.every().day.at("10:00").do(job)


while True:
    schedule.run_pending()
    print("Scheduling is running...")
    time.sleep(1)