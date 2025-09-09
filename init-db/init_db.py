import os
import pymysql
from sqlalchemy import Integer, create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
import datetime, uuid

Base = declarative_base()

class File(Base):
    __tablename__ = 'files'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)           # ex: /files/<file_id>.csv
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    downgraded_transaction = Column(Integer, default=0)

class Report(Base):
    __tablename__ = 'reports'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_file_id = Column(String(36), ForeignKey('files.id'), nullable=False)  # id-ul fișierului sursă
    path = Column(String(255), nullable=False)           # ex: /reports/<report_id>.csv
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))

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
    print("Report table ensured.")

if __name__ == "__main__":
    create_database_and_tables()
