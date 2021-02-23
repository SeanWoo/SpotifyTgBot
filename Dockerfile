FROM python:3.8
EXPOSE 5000
RUN apt-get update
WORKDIR /usr/src/tgbot
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python","server.py"]
