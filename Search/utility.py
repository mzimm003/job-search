from requests_html import (
    HTMLSession
)
from typing import (
    Dict
)
import requests_html

import urllib.parse
import urllib3
import ssl

'''Generously provided by:
https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
To address dated server side SSL (e.g. governmentjobs.com).
WARNING: Legacy server connection leaves possibility of MITM attack descrived here:
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2009-3555
'''
class CustomHttpAdapter (requests_html.requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests_html.HTMLSession()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session
'''end https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled'''

def request(searchReq:Dict):
    # ses = HTMLSession()
    ses = get_legacy_session()
    return ses.request(**searchReq)

def getlinks(
        webpageResp:requests_html.HTMLResponse,
        jobKeyword:str,
        pageKeyword:str,
        followPages:bool=True):
    l = []
    for link in webpageResp.html.absolute_links:
        if jobKeyword in link:
            l.append(link)
        if followPages and pageKeyword in link:
            pageq = urllib.parse.urlparse(link).query
            l.extend(getlinks(
                        webpageResp.session.request('GET',
                                                    webpageResp.url+'&'+pageq,
                                                    headers=webpageResp.request.headers),
                        jobKeyword,
                        pageKeyword,
                        False))

    return l

def getDesc(
        webpageResp:requests_html.HTMLResponse,
        keyword:str):
    return webpageResp.html.find(keyword)[0].text