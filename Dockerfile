FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages python3 python3-pip git dnsutils && \
	cd /opt/ && \
	git clone https://github.com/theMiddleBlue/myLittlePuny.git && \
	cd myLittlePuny && pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/opt/myLittlePuny/myLittlePuny.py"]
