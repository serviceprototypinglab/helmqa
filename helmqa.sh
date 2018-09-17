python3 main.py

mkdir logs

unameOut="$(uname -s)"

case "${unameOut}" in
    Linux*) LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_APP=helmqaweb.py flask run --host=0.0.0.0 2>&1 | tee -a logs/helmqaweb.log;;
    Darwin*) LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 FLASK_APP=helmqaweb.py flask run --host=0.0.0.0 2>&1 | tee -a logs/helmqaweb.log;;
esac