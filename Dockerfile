# prep  »» git status --ignored --porcelain
# build »» docker build -t helmqa .
# run   »» docker run -ti -p 5000:5000 -u 12345 helmqa [-s|-r]
# export»» clone to clean directory first, then: docker tag & push ...

FROM python:slim

RUN \
	apt-get update && \
	apt-get --assume-yes install --no-install-recommends git wget ca-certificates diffstat python-tk graphviz

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
	chmod 777 /home/helmqa/logs && \
	chmod 777 /home/helmqa

RUN \
     cd /home/helmqa && \
     pip3 install -r requirements.txt

EXPOSE 5000

WORKDIR /home/helmqa

# Starts HelmQA in client mode. To start HelmQA in research mode, add -r. For shell access, add -s.
ENTRYPOINT ["/bin/bash", "helmqa.sh"]
CMD []
