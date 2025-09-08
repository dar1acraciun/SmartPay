
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
import uuid

Base = declarative_base()

class File(Base):
    __tablename__ = "files"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    path = Column(String(255),default="tbd")           # ex: /files/<file_id>.csv
    timestamp = Column(DateTime)

    def insert_file(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)
        self.path = f"/files/{self.id}.csv"
        session.commit()
        return self

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