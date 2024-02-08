#!/bin/sh
set -e

CERTFILE=./app/ssl/$CERT_FILE
KEYFILE=./app/ssl/$KEY_FILE

if [ -f "$CERTFILE" ];
    
then

    echo "\033[36m[INFO]\033[m - Reading $CERTFILE file"
    echo "\033[32m[OK]\033[m - $CERTFILE Readed"

    if [ -f "$KEYFILE" ];
    
    then

        echo "\033[36m[INFO]\033[m - Reading $KEYFILE file"
        echo "\033[32m[OK]\033[m - $KEYFILE Readed"

        if $ASYNC_APP;


        then

            echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
            gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --certfile=$CERTFILE --keyfile=$KEYFILE --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app

        else

            echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
            gunicorn -w 1 --certfile=$CERTFILE --keyfile=$KEYFILE --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app

        fi
        
    else
        echo "\033[33m[WARNING]\033[m - $KEYFILE Not Found service without SSL Certificate"

        if $ASYNC_APP;


        then

            echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
            gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app

        else

            echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
            gunicorn -w 1 --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app
        
        fi
    fi

else

    echo "\033[33m[WARNING]\033[m - $CERTFILE Not Found service without SSL Certificate"

    if $ASYNC_APP;


    then

        echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
        gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app

    else

        
        echo "\033[36m[INFO]\033[m - ASYNC MODE: $ASYNC_APP"
        gunicorn -w 1 --threads $APP_THREADS -b 0.0.0.0:$APP_PORT wsgi:app

    fi
fi