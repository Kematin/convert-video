FROM python:3.10

WORKDIR /convert_bot

COPY requirements.txt /convert_bot
RUN pip install --upgrade pip && pip install -r /convert_bot/requirements.txt

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

ADD ./ /convert_bot

CMD [ "python", "src/bot.py" ]
