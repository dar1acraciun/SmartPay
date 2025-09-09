FROM python:3.11-slim

WORKDIR /init-db

COPY init-db/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ ./model/
COPY init-db/init_db.py ./init_db.py

CMD ["python", "init_db.py"]