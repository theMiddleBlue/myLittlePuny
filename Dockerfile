FROM ubuntu:latest

RUN apt-get update && \
	apt-get install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages python3 python3-pip git dnsutils locales && \
	cd /opt/ && \
	git clone https://github.com/theMiddleBlue/myLittlePuny.git && \
	cd myLittlePuny && pip3 install -r requirements.txt

RUN locale-gen en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT ["python3", "/opt/myLittlePuny/myLittlePuny.py"]
