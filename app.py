
#https://github.com/DataTeaser/textteaser
#TextTeaser is an automatic summarization algorithm.
from textteaser import TextTeaser

#https://github.com/rodricios/eatiht
#web article extraction
import eatiht.v2 as v2

import sys
import re
import urllib2, httplib
from bs4 import BeautifulSoup
from datetime import datetime
import treq
from klein import Klein
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import defer, threads
from twisted.web.static import File
import json

#keywords extraction
#https://github.com/summanlp/textrank

#from summa.summarizer import summarize
from summa import keywords

cache = {}
app = Klein()

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.route('/', branch=True)
def hello(request):
    return File('./static/')

@app.route('/feed', branch=True)
def feed(request):
    return File('./static/feed.html')


@app.route('/top', methods = ['GET'])
def top(request):
   print '/top requst args', request.args
   d = treq.get('https://hacker-news.firebaseio.com/v0/topstories.json')
   d.addCallback(treq.content)
   return d

@app.route('/story/<item_id>', methods = ['GET'])
def item(request, item_id):
   print '/story requst args', request.args
   d = treq.get('https://hacker-news.firebaseio.com/v0/item/' + item_id + '.json')
   d.addCallback(treq.content)
   return d

@app.route('/flag', methods = ['GET'])
def flag(request):
   print '/story requst args', request.args
   url = request.args.get('url')[0]
   
   if url:
      print 'url=', url
      entry = cache[url]
      print 'entry ', entry
      old = json.loads(entry)
      old['text'] = ''
      cache[url] = json.dumps(old)

   return "flagged: url" + url

@app.route('/summary', methods = ['GET', 'POST'])
@inlineCallbacks
def summary(request):
   request.setHeader('Content-Type', 'application/json')
   url = request.content.read()

   if not url:
       raise InvalidUsage('request body is empty', status_code=400)

   if url in cache:
       print "cache hit for: %s" %  url
       defer.returnValue(cache[url])
   else:
       try:
           title = yield threads.deferToThread(get_title, url)
           summary = yield threads.deferToThread(main, url, title)

           if len(summary) > 0:
               keywords = yield threads.deferToThread(get_keywords, summary)
               cache[url] = json.dumps({'title': title, 'text': summary, 'keywords': keywords})
               defer.returnValue(cache[url])
           else:
               cache[url] = json.dumps({'title': title, 'text': '', 'keywords': ''})
               defer.returnValue(cache[url])
       except Exception, e:
           e = sys.exc_info()[0]
           print "Exception : %s url = %s" %  (str(e), url)
           cache[url] = json.dumps({'title': '', 'text': '', 'keywords': ''})
           defer.returnValue(cache[url])

       defer.returnValue(200)
   #except:
      # e = sys.exc_info()[0]
       #raise InvalidUsage("server error: " + str(e), status_code=500)
'''
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
'''

'extract title from web page'
def get_title(url):
  reload(sys)
  sys.setdefaultencoding("utf-8")
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
  urllib2.install_opener(opener)
  req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7' })
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'html.parser')
  #texts = soup.findAll(text=True)
  return soup.title.string

def get_keywords(text):
  #print 'keywords:'
  keywordz = keywords.keywords(text, words=5)
  keyz = sorted(keywordz.split(), key=len)

  to_remove = []
  for key in keyz:
      for key2 in keyz:
          if len(key2) > len(key) and key in key2:
              to_remove.append(key2)

  return ', '.join(list(set(keyz) - set(to_remove)))

def main(url, title):
  print ' start processing ', url, '\n'
  text = v2.extract(url)
  tt = TextTeaser()
  sentences = tt.summarize(title, text)
  return ' '.join(sentences)
if __name__ == "__main__":
  app.run("0.0.0.0", 80)
