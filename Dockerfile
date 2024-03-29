FROM python:3.10-slim
COPY requirements.txt ./requirements.txt
COPY . ./
RUN pip install -r requirements.txt
EXPOSE 8080
CMD gunicorn -b 0.0.0.0:8080 app:server