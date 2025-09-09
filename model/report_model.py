
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, ForeignKey
import uuid

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_file = Column(String(36), ForeignKey("files.id"), nullable=False)
    path = Column(String(255),default="tbd")           # ex: /reports/<report_id>.csv
    timestamp = Column(DateTime)

    def insert_report(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)
        self.path = f"/reports/{self.id}.csv"
        session.commit()
        return self

    @staticmethod
    def get_report(session, report_id):
        return session.query(Report).filter_by(id=report_id).first()

    @staticmethod
    def get_reports(session):
        return session.query(Report).all()

    @staticmethod
    def delete_report(session, report_id):
        report = session.query(Report).filter_by(id=report_id).first()
        if report:
            session.delete(report)
            session.commit()
            return True
        return False
    