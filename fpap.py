#!/usr/bin/python
# -*- coding: utf-8 -*-

import facebook
import random
import urllib, urlparse
import cookielib
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import sys
import csv
import json


google_username        = '*'
google_password        = '*'
spreadsheet_id         = '*' # document id - you can get it from URL
worksheet_id           = 'od6' # for 1st worksheet

CSV_DELIMETER = ';'

APPID = "*"
APPSECRET = "*" # fb appsecret, you need to create a fb app
  
''' page access tokens: to get they do this:
    Go to the Graph API Explorer
    Choose your app from the dropdown menu
    Click "Get Access Token"
    Choose the manage_pages permission (you may need the user_events permission too, not sure)
    Now access the me/accounts connection and copy your page's access_token
    Click on your page's id
    Add the page's access_token to the GET fields '''

 # {pageid : page_token}   
page_tokens = {
'*':'*',
}
class GoogleSpreadsheet():
	''' An iterable google spreadsheet object.  Each row is a dictionary with an entry for each field, keyed by the header.  GData libraries from Google must be installed.'''
	
	def __init__(self, spreadsheet_id, worksheet_id, username , password, source=''):
		gd_client = gdata.spreadsheet.service.SpreadsheetsService()
		gd_client.email = username 
		gd_client.password = password
		gd_client.source = source
		gd_client.ProgrammaticLogin()
		
		self.count = 0
		self.rows = self.formRows(gd_client.GetListFeed(spreadsheet_id, worksheet_id))
		
	def formRows(self, ListFeed):
		rows = []
		for entry in ListFeed.entry:
			d = {}
			for key in entry.custom.keys():
				d[key] = entry.custom[key].text
			rows.append(d)
		return rows
			
	def __iter__(self):
		return self
		
	def next(self):
		if self.count >= len(self.rows):
			self.count = 0
			raise StopIteration
		else:
			self.count += 1
			return self.rows[self.count - 1]
	
	def __getitem__(self, item):
		return self.rows[item]
		
	def __len__(self):
		return len(self.rows)
        

           
class Post():                                               #used to post something
    def __init__(self, text):
        self.link = text
    def post(self, appid, appsecret, pageid, page_access_token):
        oauth_arspreadsheet = dict(client_id     = appid,
              client_secret = appsecret,
              grant_type    = 'client_credentials')

        oauth_response = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_arspreadsheet)).read()
        try:
            oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
        except KeyError:
            raise
        
        attach = {
            "name": '',
            "link": self.link,
            "caption": '',
            "description": '',
            "picture" : '',
            }
        
        graph = facebook.GraphAPI(page_access_token)
        try:
            response = graph.put_wall_post('', attachment=attach)
            print "--- Ok!"
            print ''
        except facebook.GraphAPIError as e:
            print e
            
    def isExist(self, appid, appsecret, pageid, page_access_token):   
        oauth_arspreadsheet = dict(client_id     = appid,
              client_secret = appsecret,
              grant_type    = 'client_credentials')

        oauth_response = urllib.urlopen('https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_arspreadsheet)).read()
        try:
            oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
        except KeyError:
            raise       
            
        graph = facebook.GraphAPI(page_access_token)
        postlist = None
        try:
            d = json.load(urllib.urlopen('https://graph.facebook.com/?ids=https://www.facebook.com/'+pageid))
            p = d[d.keys()[0]]["id"]
            postlist = graph.get_object(p+'/feed')
        except facebook.GraphAPIError as e:
            print e         
            
        linklist = []
        for post in postlist[u'data']:
            try:
                linklist.append(post[u'link'])
            except:
                pass
        if self.link in linklist:
            return True
        else:
            return False
        
def postloop(row, postlistkeys):        
    i = 0
    while i <= 10:
        text = getrandomtext(row, postlistkeys)
        print "--- Trying to post random item : %s" % text
        p = Post(text)
        if not p.isExist (APPID, APPSECRET, pageid, page_tokens[pageid]):
            p.post(APPID, APPSECRET, pageid, page_tokens[pageid])
            break
        i += 1
 
def getrandomtext(row, postlistkeys):
    text = ''
    i = 100
    while len(text) < 2 or i > 0:
        text = row[random.choice(postlistkeys)]
        if text == None:
            text = '' 
        i -= 1    
    return text        

       
if len(sys.argv) < 3:
    print "USAGE %s Number of row (integer)|ALL file.csv|GOOGLE" % sys.argv[0]
    sys.exit()
    
if sys.argv[1] == 'ALL':
    allflag = True
else:
    try:
        allflag = False
        i = int(sys.argv[1])
    except:
        print "USAGE %s Number of row (integer)|ALL file.csv|GOOGLE" % sys.argv[0]
        sys.exit()   

if sys.argv[2] == 'GOOGLE':
    googleflag = True
else:    
    try:
        googleflag = False
        filename = sys.argv[2]
    except:
        print "USAGE %s Number of row (integer)|ALL file.csv|GOOGLE" % sys.argv[0]
        sys.exit()           



if googleflag:
    keyword_key = 'keyword'
    fanpageurl_key = 'fanpageurl'
    try:
        spreadsheet = GoogleSpreadsheet(spreadsheet_id, worksheet_id, google_username, google_password)
    except Exception:
        print 'No access to Google spreadsheet!'
        sys.exit()
else:
    keyword_key = 'Keyword'
    fanpageurl_key = 'Fan Page URL'
    spreadsheet = []
    with open (filename, 'rU') as csvfile:
        _spreadsheet = csv.DictReader(csvfile, delimiter=CSV_DELIMETER)
        for row in _spreadsheet:
            spreadsheet.append(row)
            
          
          
            
if not allflag:        
    if i > len(spreadsheet)-1:         # no such row
        print "There are only %d data rows in spreedsheet, and you trying to work with row #%d" % (len(spreadsheet)-1, i)
        sys.exit()
        
    
    print 'Working with row %d : %s' % (i,spreadsheet[i][keyword_key])        
    possibly_pageid = spreadsheet[i][fanpageurl_key].split("/")[-1]  # last element of URL - usually a page id
    
    
    if  possibly_pageid in page_tokens:                   #trying to find page access token
        pageid = possibly_pageid                        
    else:
        print 'Page ID %s not found at page_tokens dictionary' % possibly_pageid
        sys.exit()
    
    print 'Facebook fan page url : %s' % spreadsheet[i][fanpageurl_key]
    postlistkeys = spreadsheet[i].keys();
    postlistkeys.remove(keyword_key)
    postlistkeys.remove(fanpageurl_key)
    postloop()
    
else:
    for row in spreadsheet:
        possibly_pageid =  row[fanpageurl_key].split("/")[-1]  # last element of URL - usually a page id
        
        
        if  possibly_pageid in page_tokens:                   #trying to find page access token
            pageid = possibly_pageid          
        else:
            print 'Page ID %s not found at page_tokens dictionary' % possibly_pageid            
            sys.exit()
                
        print 'Facebook fan page url : %s' % row[fanpageurl_key]
        postlistkeys = row.keys();
        postlistkeys.remove(keyword_key)
        postlistkeys.remove(fanpageurl_key)
        postloop(row, postlistkeys)



            
        

