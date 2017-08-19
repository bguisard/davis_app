NUM_WORKERS=1
NUM_THREADS=2
BIND_ADDRESS=127.0.0.1:8080
CERTFILE='cert.pem'
KEYFILE='key.pem'
TIMEOUT=1200
GRACEFUL=1200
LOGFILE='./logs/gunicorn.log'
WORKER_CLASS='gevent'
IP_LIST='10.30.95.2'


gunicorn --worker-class gevent \
         -w $NUM_WORKERS \
         -b $BIND_ADDRESS \
         --threads $NUM_THREADS \
         -t $TIMEOUT \
         --graceful-timeout $GRACEFUL \
         --error-logfile $LOGFILE \
         --forwarded-allow-ips $IP_LIST \
         wsgi:app
