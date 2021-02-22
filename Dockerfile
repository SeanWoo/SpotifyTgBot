FROM python:3.8
WORKDIR /usr/src/tgbot
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python","/usr/src/tgbot/server.py"]
