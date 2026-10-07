import time
from datetime import datetime

import schedule
from script import run_stock_job


def basic_job():
    print("Job started at:", datetime.now())


def safe_run_stock_job():
    try:
        run_stock_job()
    except Exception as exc:
        print(f'stock job failed: {exc}')


schedule.every().minute.do(basic_job)
schedule.every().minute.do(safe_run_stock_job)

while True:
    schedule.run_pending()
    time.sleep(1)
