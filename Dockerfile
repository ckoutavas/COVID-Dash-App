FROM python:3.10-slim
RUN pip install -r requirements.txt
CMD gunicorn --memory 500m --timeout 600 --bind 0.0.0.0:8050 app:server
EXPOSE 8050