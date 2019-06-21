if [ "$1" == "-r" ]; then
	echo " * HelmQA research (analysis) mode"
	python3 main.py &
elif [ "$1" == "-s" ]; then
	echo " * Shell (debug) mode"
	/bin/sh
	exit
else
	if [ -d /charts ]
	then
		echo " * HelmQA client (local charts) mode"
		python3 main.py
		exit
	else
		echo " * HelmQA client (CI/CD) mode"
	fi
fi

mkdir -p logs

unameOut="$(uname -s)"

case "$unameOut" in
    Linux*) LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_APP=helmqaweb.py flask run --host=0.0.0.0 2>&1 | tee -a logs/helmqaweb.log;;
    Darwin*) LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 FLASK_APP=helmqaweb.py flask run --host=0.0.0.0 2>&1 | tee -a logs/helmqaweb.log;;
esac
