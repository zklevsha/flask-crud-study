FROM python:3.8-alpine

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app.py .

EXPOSE 80

CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]