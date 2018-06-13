# build »» docker build -t helmqa .
# run   »» docker run -ti -p 5000:5000 -u 12345 helmqa /bin/sh

FROM debian:stretch

RUN \
	apt-get update && \
	apt-get --assume-yes install --no-install-recommends python3-yaml python3-flask python3-pkg-resources wget ca-certificates diffstat

# RUN apt-get --assume-yes install --no-install-recommends python3-pyqt5.qtwebengine python3-lxml python3-matplotlib python3-seaborn xvfb

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

EXPOSE 5000

#CMD ["/bin/sleep", "9999999"]
CMD ["/bin/sh", "/home/helmqa/helmqaweb.sh"]
