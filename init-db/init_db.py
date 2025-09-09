import os
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

    # Ensure database exists (conectare ca userul aplicației)
    conn = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password)
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
