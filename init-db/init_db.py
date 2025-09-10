import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
from sqlalchemy import create_engine
from model.file_model import File
from model.report_model import Report
from model.base import Base

def create_database_and_tables():
    db_host = os.getenv('MYSQL_HOST', 'db')
    # în Docker network MySQL ascultă pe 3306; pe host folosești 3307
    db_port = int(os.getenv('MYSQL_PORT', '3306'))
    db_user = os.getenv('MYSQL_USER', 'smartuser')
    db_password = os.getenv('MYSQL_PASSWORD', 'smartpass')
    db_name = os.getenv('MYSQL_DATABASE', 'smartpay')


    # Retry loop: wait for MySQL to be ready
    import time
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password)
            break
        except Exception as e:
            print(f"[init-db] Attempt {attempt+1}/{max_attempts}: MySQL not ready ({e}), retrying in 2s...")
            time.sleep(2)
    else:
        raise RuntimeError("[init-db] Could not connect to MySQL after waiting.")

    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' ensured.")

    DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(DATABASE_URL, echo=True, future=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("File și Report tables ensured.")

if __name__ == "__main__":
    create_database_and_tables()
