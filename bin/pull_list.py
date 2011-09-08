#!/usr/bin/env python
"""
A simple script that scarpes your Pull List from ComiXology.

HOWTO:
	
	$ python pull_list.py mylesb
	Daken: Dark Wolverine #8
	Hellboy: Buster Oakley Gets His Wish
	The Li'l Depressed Boy #3
	Marvel's Greatest Comics: Ultimate Fantastic Four #1
	
	or 
	$ python pull_list.py http://www.comixology.com/thisweek/
	Charismagic #0 2nd Ptg
	Flash Gordon Comic Book Archives Vol. 3 HC
	The Goon vs. Mr Wicker Mens: LG
	The Goon W/ Logo Mens: MED
	The Goon W/ Logo Mens: LG
	...
	

Copyright (c) 2010, Myles Braithwaite <me@mylesbraithwaite.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution.

* Neither the name of the Monkey in your Soul nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import re
import sys
import urllib2
from BeautifulSoup import BeautifulSoup

__version__ = '0.1'
__project_name__ = 'PullListScraper'
__project_link__ = 'http://gist.github.com/914073'

COMIXOLOGY_PULL_LIST_URL = 'http://www.comixology.com/user/%s/pulllist/?f=COMIC'

def get_html(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', '%s/%s +%s' % (
		__project_name__, __version__, __project_link__
	))
	opener = urllib2.build_opener()
	return opener.open(request).read()

def get_pages(soup):
	page_num_urls = [ ]
	
	browse_items = soup.find('div', attrs={'id': 'browse'})
	
	if not browse_items:
		return page_num_urls
	
	for page in browse_items.findAll('a'):
		page_num_urls += [ page['href'], ]
	
	return page_num_urls

def get_pull_items(soup):
	listings = soup.find('div', attrs={'id': 'list-items'})
	
	pull_items = listings.findAll('table')
	
	for comic in pull_items:
		title = comic.find('div', attrs={'id': 'title'}).findAll('a')[1].text
		link = 'http://www.comixology.com' + comic.find('div', attrs={'id': 'title'}).findAll('a')[1]['href']
		try:
			price = re.search('.*?(\\$[0-9]+(?:\\.[0-9][0-9])?)(?![\\d])', comic.find('div', attrs={'class': 'specs'}).text).group(1)
		except AttributeError:
			price = None
		description = comic.find('div', attrs={'id': 'description'}).find('div', attrs={'class': 'body'}).text.strip('(more)')
		template = """%(title)s - %(price)s\n\t%(description)s\n%(link)s\n"""
		print template % {
			'title': title,
			'link': link,
			'price': price,
			'description': description
		}

def main(url):
	if not url.startswith('http://'):
		url = COMIXOLOGY_PULL_LIST_URL % url
	html = get_html(url)
	soup = BeautifulSoup(html)
	
	print "Pull List for %s.\n" % soup.find('h2').find('strong').text
	
	get_pull_items(soup)
	
	pages = get_pages(soup)
	
	for page in pages:
		html = get_html(url + page)
		soup = BeautifulSoup(html)
		get_pull_items(soup)

if __name__ == "__main__":
	try:
		url = sys.argv[1]
	except IndexError:
		url = 'http://www.comixology.com/thisweek/?f=COMIC'
	main(url)
