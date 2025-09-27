FROM python:3.13-alpine3.21



COPY requirements.txt scripts/aurelius_entrypoint.sh .
COPY bot/ ./bot/
COPY database_services/ ./database_services/
COPY utils/ ./utils/


RUN pip install -r requirements.txt


ENTRYPOINT ["./aurelius_entrypoint.sh"]