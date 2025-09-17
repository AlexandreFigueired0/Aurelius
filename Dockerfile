FROM python:3.13-alpine3.21


COPY requirements.txt main.py database_service.py  scripts/aurelius_entrypoint.sh .

COPY utils/ ./utils/

RUN pip install -r requirements.txt


ENTRYPOINT ["./aurelius_entrypoint.sh"]