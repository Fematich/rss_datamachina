from __future__ import unicode_literals

from datetime import datetime
import dateutil.parser
import dateutil.tz
import pytz,requests,urllib2,os, logging
from bs4 import BeautifulSoup

from google.appengine.ext import ndb
import cloudstorage as gcs

from feedgen.feed import FeedGenerator

from flask import Flask,redirect, Response

from config import hdr,bucket_name

app = Flask(__name__)

write_retry_params = gcs.RetryParams(backoff_factor=1.1)

class datamachinatimestamp(ndb.Model):
    last_date = ndb.StringProperty()

@app.route('/cron/datamachina')
def crondatamachina():
    datamachina_key = ndb.Key(urlsafe="ahNzfnJlYWRpbmdhdXRvbWF0aW9uci4LEhRkYXRhbWFjaGluYXRpbWVzdGFtcCIUZGF0YW1hY2hpbmF0aW1lc3RhbXAM").get(use_cache=False, use_memcache=False)
    def parseWeek(url,date):
        date = dateutil.parser.parse(date).replace(tzinfo=pytz.utc)
        response = urllib2.urlopen(url)
        html_week = response.read()
        soup_week = BeautifulSoup(html_week, 'html.parser')
        for link in soup_week.find_all('a'):
            if(link.get_text()==u'Invite your friends to Data Machina'):
                break
            if(link.get_text()!=u'@ds_ldn'):
                #print link.get_text()
                #print(link.get_text(),link.get('href'))
                fe = fg.add_entry()
                fe.id(link.get('href'))
                fe.title(link.get_text())
                fe.guid(link.get('href'))
                fe.updated(date)
                fe.published(date)
                fe.link({"href":link.get('href')})
                try:
                    text=BeautifulSoup(requests.get(link.get('href'),
                                                              headers=hdr,
                                                              verify=False).text, 'html.parser').find('p').getText()
                    fe.description(text)
                except Exception,e:
                    print e    
    
    response = urllib2.urlopen('http://tinyletter.com/datamachina/archive?page=&recs=5&sort=desc')
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    fg = FeedGenerator()
    fg.id('https://pbs.twimg.com/profile_images/1787151199/dsldn_normal.jpg')
    fg.title('Data Machina RSS feed')
    fg.link( href='http://tinyletter.com/datamachina', rel='alternate' )
    fg.logo('https://pbs.twimg.com/profile_images/1787151199/dsldn_normal.jpg')
    fg.subtitle('RSS feed containing all the links from the last data machina mail')
    fg.link( href='http://bit.ly/datamachina', rel='self' )
    fg.language('en')
    for link in soup.find_all('a'):
        if "week" in link.get('href'):
            #print "+"*50+"\n"+link.get_text()+"\n"+"+"*50
            date=link.previousSibling.previousSibling.get_text()
            if(datamachina_key.last_date==date):
                return 'datamachina cached', 200
            else:
                #update last_date
                datamachina_key.last_date=date
                datamachina_key.put()
                #parse content
                parseWeek(link.get('href'),date)
            break
    rssfeed  = fg.rss_str(pretty=True)
    
    filename="/"+bucket_name+"/data/datamachina.rss"
    gcs_file = gcs.open(filename,
                      'w',
                      content_type='text/plain',
                      retry_params=write_retry_params#,
                      #options={'x-goog-acl': 'public-read'} #public sharing not working
         )
    gcs_file.write(rssfeed)
    gcs_file.close()
    return 'datamachina refresh', 200

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500