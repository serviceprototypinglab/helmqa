# build »» docker build -t helmqa .
# run   »» docker run -ti -p 5000:5000 -u 12345 helmqa /bin/sh

FROM python:stretch

RUN \
	apt-get update && \
	apt-get --assume-yes install --no-install-recommends wget ca-certificates diffstat

RUN \
	wget --no-check-certificate https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz && \
	tar xvf helm-v2.9.1-linux-amd64.tar.gz && \
	mv linux-amd64/helm /usr/local/bin && \
	rm -rf helm-*.tar.gz linux-amd64

COPY . /home/helmqa

RUN \
	useradd helmqa && \
	chown -R helmqa /home/helmqa

RUN \
	mkdir /home/helmqa/logs && \
	chmod 777 /home/helmqa/logs && \
	chmod 777 /home/helmqa

RUN \
     cd /home/helmqa && \
     pip3 install -r requirements.txt

EXPOSE 5000

#CMD ["/bin/sleep", "9999999"]
WORKDIR /home/helmqa
CMD ["/bin/sh", "/home/helmqa/helmqa.sh"]
