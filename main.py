from google.appengine.ext import webapp
from google.appengine.api import urlfetch
import urllib2
import time
import logging, datetime

def remove_www(handler):
    if handler.request.url.startswith('http://www.'):
        handler.redirect(handler.request.url.replace('http://www.', 'http://'))

def makeStatic(template_name, context={}):
    class Static(webapp.RequestHandler):
        def get(self):
            remove_www(self)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(
                render(template_name, context)
            )
    return Static

import re
# Allow 'abc' and 'abc.def' but not '.abc' or 'abc.'
valid_callback = re.compile('^\w+(\.\w+)*$')

from BeautifulSoup import BeautifulSoup

class twitpicapi(webapp.RequestHandler):
    user = ""
    ids = []
    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        callback = self.request.get('callback', default_value='')
        page = self.request.get('page', default_value='0')
        self.user = self.request.path[1:]
        
        self.loadTwitPicPage(page)
        
        json = []
        for j in self.ids:
            json.append("{ id : '%s', url : '%s', twitpic_url : '%s', date : '%s', title : '%s' }" % (j['id'], j['url'], j['twitpic_url'], j['date'], re.escape(j['title'])))
        
        # json = u"{ works : false, user : '%s', id_size : %s }" % (self.user, len(self.ids))
        json = '[%s]' % (",\n".join(json))
        if callback and valid_callback.match(callback):
            json = '%s(%s)' % (callback, json)
        self.response.out.write(json)

    def loadTwitPicPage(self, page):
        url = ""
        if page > 1:
            url = 'http://twitpic.com/photos/%s?page=%s' % (self.user, page)
        else:
            url = 'http://twitpic.com/photos/%s' % (self.user)
        
        # self.response.out.write('Grabbing from ' + url + "\n")
        contents = urllib2.urlopen(url)
        soup = BeautifulSoup(contents)
        for photowrapper in soup('div', {"class":"profile-photo-img"}):
            json = {}
            anchor = photowrapper.find('a')
            json['id'] = anchor['href'][1:]
            json['twitpic_url'] = 'http://twitpic.com/show/large/' + json['id']
        
            image = urlfetch.fetch(url=json['twitpic_url'], follow_redirects=False)
            if image.status_code == 302:
                json['url'] = image.headers['location']
            else:
                json['url'] = json['twitpic_url']
        
            # required to get the date - sucks that they don't maintain the date on the image URL
            twitpicPage = urllib2.urlopen('http://twitpic.com/' + json['id'])
            twitpicPageSoup = BeautifulSoup(twitpicPage)
            meta = twitpicPageSoup.find('div', { "id" : "photo-info" }).find('div').contents[0].strip() # grab the first nest div
            date = time.strptime(meta,"Posted on %B %d, %Y")
            json['date'] = time.strftime("%Y-%m-%d", date)

            json['title'] = ''
            if (twitpicPageSoup.find('div', { 'id' : 'view-photo-caption' }) is not None):
                json['title'] = twitpicPageSoup.find('div', { 'id' : 'view-photo-caption' }).contents[0].strip()

            self.ids.append(json)
        
        # if soup.find(text=re.compile("OLDER")):
        #     href = soup.find(text=re.compile("OLDER")).parent['href']
        #     m = re.search('(\d+?)$', href)
        #     if m is not None:
        #         self.loadTwitPicPage(m.group(0))

class Http404Page(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.error(404)
        self.response.out.write(render('index.html', {
            'path': self.request.path,
        }))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    from wsgiref.handlers import CGIHandler
    application = webapp.WSGIApplication([
        ('/', makeStatic('index.html')),
        (r'/[a-z0-9]{1,15}$', twitpicapi),
        ('/.*$', Http404Page),
    ], debug=True)
    CGIHandler().run(application)

import os
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
from google.appengine.ext.webapp import template
def render(template_name, context={}):
    path = os.path.join(template_dir, template_name)
    return template.render(path, context)

if __name__ == "__main__":
    main()