NUM_WORKERS=1
NUM_THREADS=2
BIND_ADDRESS=0.0.0.0:5000
CERTFILE='cert.pem'
KEYFILE='key.pem'
TIMEOUT=1200
GRACEFUL=1200
LOGFILE='./logs/gunicorn.log'
WORKER_CLASS='gevent'


gunicorn --worker-class gevent \
         -w $NUM_WORKERS \
         -b $BIND_ADDRESS \
         --threads $NUM_THREADS \
         -t $TIMEOUT \
         --graceful-timeout $GRACEFUL \
         --certfile $CERTFILE \
         --keyfile $KEYFILE \
         --do-handshake-on-connect \
         --error-logfile $LOGFILE \
         wsgi:app
