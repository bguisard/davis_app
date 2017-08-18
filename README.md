# DAVIS: Deep Learning Analytics for Video Streams

## Web App

This repo contains the web app that serves  Davis, for the full model please visit Davis main [repo](https://github.com/bguisard/davis).


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
