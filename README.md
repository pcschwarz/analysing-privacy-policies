# How to access the dashboard on the web

Just open the following URL (it might take a while the first time you run it, as the dashboard gets redeployed after its not been used for over an hour)
https://vagueness-and-readability.herokuapp.com/

# How to run the services on your own

there are several options how to run the dashboard.

## gunicorn way

use the command:  gunicorn app:server -b :8050

## docker way

Dependencies: Install docker and docker-compose on your device. 

To run the application, `cd` into this directory and run `docker-compose up`.
The dashboard service and the website will start (if necessary, docker-compose will automatically build

if you want to rebuild the container, in case you changed something try the command:
docker-compose up -d --force-recreate --build


You can also open the whole project in pycharm and simply run app.py.

# How to use the running services

Open localhost:8050 (local-testrun) or localhost:8051 (when you use it via docker) in your browser.
