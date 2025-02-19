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

"""
RogerThis - 16/8/2011
Site: http://www.vidxden.com , http://www.divxden.com & http://www.vidbux.com
vidxden hosts both avi and flv videos
In testing there seems to be a timing issue with files coming up as not playable.
This happens on both the addon and in a browser.
"""

import re
import urllib2
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class VidxdenResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vidxden"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, web_url):
        """ Human Verification """
        try:
            resp = self.net.http_GET(web_url)
            html = resp.content
            post_url = resp.get_url()

            form_values = {}
            for i in re.finditer('<input name="(.+?)".+?value="(.+?)"', html):
                form_values[i.group(1)] = i.group(2)

            html = self.net.http_POST(post_url, form_data=form_values).content

        except urllib2.URLError, e:
            common.addon.log_error('vidxden: got http error %d fetching %s' %
                                  (e.code, web_url))
            return False
        
        #find packed javascript embed code     
        r = re.search('return p}\(\'(.+?);\',\d+,\d+,\'(.+?)\'\.split',html)
        if r:
            p, k = r.groups()
        else:
            common.addon.log_error('vidxden: packed javascript embed code not found')

        decrypted_data = unpack_js(p, k)
        
        #First checks for a flv url, then the if statement is for the avi url
        r = re.search('file.\',.\'(.+?).\'', decrypted_data)
        if not r:
            r = re.search('src="(.+?)"', decrypted_data)
        if r:
            stream_url = r.group(1)
        else:
            common.addon.log_error('vidxden: stream url not found')
            return False

        return stream_url

        
    def valid_url(self, web_url):
        return re.match('http://(?:www.)?(vidxden|divxden|vidbux).com/' +
                        '(embed-)?[0-9a-z]+', web_url)
        
        
def unpack_js(p, k):
    '''emulate js unpacking code'''
    k = k.split('|')
    for x in range(len(k) - 1, -1, -1):
        if k[x]:
            p = re.sub('\\b%s\\b' % base36encode(x), k[x], p)
    return p


def base36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Convert positive integer to a base36 string. (from wikipedia)"""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    # Special case for zero
    if number == 0:
        return alphabet[0]

    base36 = ''

    sign = ''
    if number < 0:
        sign = '-'
        number = - number

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

