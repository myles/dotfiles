#!/usr/bin/env python
"""
Downloads all image links from a web page.

Copyright (c) 2012, Myles Braithwaite <me@mylesbraithwaite.com>
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

import os
import sys
import urllib
import urllib2
import logging
import urlparse
import argparse

from BeautifulSoup import BeautifulSoup, SoupStrainer

a_links = SoupStrainer('a')

__version__ = '0.1'
__project_name__ = 'DownloadAllImageLinks'
__project_link__ = 'http://gist.github.com/'

IMAGE_ENDINGS = (
	'.jpg',
	'.png',
	'.gif',
	'.jpeg'
)

log = logging.getLogger()

def get_html(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent', '%s/%s +%s' % (
		__project_name__, __version__, __project_link__
	))
	opener = urllib2.build_opener()
	return opener.open(request).read()

def get_links(html):
	soup = BeautifulSoup(html, parseOnlyThese=a_links)
	
	links = soup.findAll('a', href=True)
	
	images = []
	
	for link in links:
		if link['href'].lower().endswith(IMAGE_ENDINGS):
			images += [ link['href'], ]
	
	return images

def download_image(page_url, image_url, output_path):
	url = urlparse.urljoin(page_url, image_url)
	log.info("Downloading %s", url)
	filename = url.split("/")[-1]
	outpath = os.path.join(output_path, filename)
	urllib.urlretrieve(url, outpath)

def main(url, output_path):
	html = get_html(url)
	images = get_links(html)
	
	for img in images:
		download_image(url, img, output_path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--url', dest='url', action='store', required=True)
	parser.add_argument('--dir', dest='dir', action='store', required=True)
	
	args = parser.parse_args()
	
	main(args.url, os.path.abspath(args.dir))