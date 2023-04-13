FROM python:3.10-slim
COPY requirements.txt ./requirements.txt
COPY . ./
RUN pip install -r requirements.txt
CMD gunicorn -b 0.0.0.0:8050 app:server
EXPOSE 8050