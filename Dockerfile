FROM python:latest

RUN mkdir log
# COPY config config
# COPY requirements.txt /
# COPY tracker.py /

COPY . .

RUN pip3 install -r requirements.txt

CMD [ "python3", "tracker.py"]