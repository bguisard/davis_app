# DAVIS: Deep Learning Analytics for Video Stream

## Web App

This repo only contains the web app part of Davis, for the full model please visit Davis main repo (add link)


## How to install

* Clone the repo and create logs folder

```
git clone https://github.com/bguisard/davis_app.git

cd davis_app

mkdir logs

```

* Issue certificates for SSL

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

* Create new virtual environment with python 2.7 and dependencies listed on requirements.txt

```
pip install -r requirements.txt
```

* Run gunicorn server

```
./run.sh
```
