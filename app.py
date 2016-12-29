
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
from flask import Flask, request, jsonify

#keywords extraction
#https://github.com/summanlp/textrank

#from summa.summarizer import summarize
from summa import keywords

from flask import Flask, request
app = Flask(__name__)

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

@app.route('/')
def hello():
    return "text summarized API"

@app.route('/summary', methods = ['GET', 'POST'])
def summary():
   url = request.data
   if not url:
       raise InvalidUsage('request body is empty', status_code=400)
   try:
       title = get_title(url)
       summary = main(url, title)
       return jsonify(title=title,
                       text=summary,
                       keywords=get_keywords(summary))
   except:
       e = sys.exc_info()[0]
       raise InvalidUsage("server error: " + str(e), status_code=500)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

'extract title from web page'
def get_title(url):
  reload(sys)
  sys.setdefaultencoding("utf-8")
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
  urllib2.install_opener(opener)
  req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1' })
  html = urllib2.urlopen(req).read()
  soup = BeautifulSoup(html, 'html.parser')
  #texts = soup.findAll(text=True)
  return soup.title.string

def get_keywords(text):
  print 'keywords:'
  keywordz = keywords.keywords(text, words=5)
  keyz = sorted(keywordz.split(), key=len)

  to_remove = []
  for key in keyz:
      for key2 in keyz:
          if len(key2) > len(key) and key in key2:
              to_remove.append(key2)

  return ', '.join(list(set(keyz) - set(to_remove)))

def main(url, title):
  print 'processing ', url, '\n'
  text = v2.extract(url)
  tt = TextTeaser()
  sentences = tt.summarize(title, text)
  return ' '.join(sentences)
if __name__ == "__main__":
  #main(sys.argv[1:])
  app.run(port = 8080, debug = True)
