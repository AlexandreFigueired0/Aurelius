FROM python:3.13-alpine3.21


COPY requirements.txt main.py database_service.py init_db.py scripts/aurelius_entrypoint.sh .

RUN pip install -r requirements.txt


ENTRYPOINT ["./aurelius_entrypoint.sh"]