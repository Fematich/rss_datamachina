## App Engine Flask Project to serve DataMachina TinyLetter archive* links as an RSS feed

This code contains two services running on App Engine and one daily cron task:

1. Default service:  This will serve the actual RSS feed, currently reading from GCS and returning the content via App Engine, the goal was to publicly share from GCS and just use a redirect. Unfortunately GCS integration with public sharing didn't work.

2. Jobs service: this will daily check the DataMachina Archive and update the RSS file on GCS if needed. We use an App Engine Cron Task to do the daily checking.


## Dependancies

Before running or deploying this application, install the dependencies using
[pip](http://pip.readthedocs.io/en/stable/):

    pip install -t lib -r requirements.txt

*http://tinyletter.com/datamachina/archive