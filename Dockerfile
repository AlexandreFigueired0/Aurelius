FROM python:3.13-alpine3.21


COPY requirements.txt companies.csv main.py database_service.py  scripts/aurelius_entrypoint.sh .
COPY utils/init_db.py utils/collect_stock_names.py ./utils

RUN pip install -r requirements.txt


ENTRYPOINT ["./aurelius_entrypoint.sh"]