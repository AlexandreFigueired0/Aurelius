FROM python:3.13-alpine3.21


COPY requirements.txt main.py database_service.py .

RUN pip install -r requirements.txt


CMD ["python3", "main.py"]