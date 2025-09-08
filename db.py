from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://smartuser:smartpass@db:3306/smartpay"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
