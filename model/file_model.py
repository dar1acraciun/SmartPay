
import json
from model.base import Base
from sqlalchemy import Column, String, DateTime, Integer
import uuid


class File(Base):
    __tablename__ = "files"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    path = Column(String(255),default="tbd")           # ex: /files/<file_id>.csv
    timestamp = Column(DateTime)
    downgraded_transaction = Column(Integer, default=0)  
    brand = Column(String(50), default="unknown")  # e.g., Visa, MasterCard, etc.

    def insert_file(self, session, brand):
        session.add(self)
        session.commit()
        session.refresh(self)
        self.path = f"/files/{self.id}.csv"
        self.brand = brand
        session.commit()
        return self

    def update_transaction(self, session, json_data):
        # Count how many transactions have downgrade == True or False
        count = sum(1 for tx in json_data.get("per_transaction", []) if tx.get("downgrade") is True)
        self.downgraded_transaction = count
        session.commit()
        session.refresh(self)
        #save in  a file the json data as string and the count
        with open(f"123333_transactions.json", "w") as f:
            json.dump(json_data, f)
            f.write(f"\nCount of downgraded transactions: {count}\n")


    @staticmethod
    def get_file(session, file_id):
        return session.query(File).filter_by(id=file_id).first()

    @staticmethod
    def get_files(session):
        return session.query(File).all()

    @staticmethod
    def delete_file(session, file_id):
        file = session.query(File).filter_by(id=file_id).first()
        if file:
            session.delete(file)
            session.commit()
            return True
        return False