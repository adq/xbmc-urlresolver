"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from t0mm0.common.net import Net
import urllib2
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class PutlockerResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "putlocker/sockshare"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
    
    def get_media_url(self, web_url):
        #find session_hash
        try:
            html = self.net.http_GET(web_url).content
        except urllib2.URLError, e:
            common.addon.log_error('putlocker: got http error %d fetching %s' %
                                    (e.code, web_url))
            return False
        r = re.search('value="([0-9a-f]+?)" name="hash"', html)
        if r:
            session_hash = r.group(1)
        else:
            common.addon.log_error('putlocker: session hash not found')
            return False

        #post session_hash
        try:
            self.net.http_POST(web_url, form_data={'hash': session_hash, 
                                          'confirm': 'Continue as Free User'})
        except urllib2.URLError, e:
            common.addon.log_error('putlocker: got http error %d posting %s' %
                                    (e.code, web_url))
            return False
        
        #find download link
        xml_url = re.sub('/(file|embed)/', '/get_file.php?stream=', web_url)
        try:
            html = self.net.http_GET(xml_url).content
        except urllib2.URLError, e:
            common.addon.log_error('putlocker: got http error %d fetching %s' %
                                    (e.code, xml_url))
            return False
        r = re.search('url="(.+?)"', html)
        if r:
            flv_url = r.group(1)
        else:
            common.addon.log_error('putlocker: stream url not found')
            return False
        
        return flv_url
        
    def valid_url(self, web_url):
        return re.match('http://(www.)?(putlocker|sockshare).com/(file|embed)' +
                        '/[0-9A-Z]+', web_url)

