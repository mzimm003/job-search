from requests_html import (
    HTMLSession
)
from functools import partial
from typing import (
    Dict,
    List,
    Callable
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

class Plan:
    def __init__(self) -> None:
        self.session = None
        self.plan = []

    @classmethod
    def HTMLJobLinksDefault(cls):
        p = cls()
        p.addToPlan('request')
        p.addToPlan('getJobLinksByHTML')
        return p
    
    @classmethod
    def HTMLJobDescDefault(cls):
        p = cls()
        p.addToPlan('request')
        p.addToPlan('getJobDescByHTML')
        return p
    
    def request(self, reqDict:Dict, **kwargs):
        return self.session.request(**reqDict)

    def getJobLinksByHTML(
            self,
            webpageResp:requests_html.HTMLResponse,
            jobKeyId:str,
            pageKeyId:str,
            followPages:bool=True,
            **kwargs):
        l = []
        for link in webpageResp.html.absolute_links:
            if jobKeyId in link:
                l.append(link)
            if followPages and pageKeyId in link:
                pageq = urllib.parse.urlparse(link).query
                l.extend(self.getJobLinksByHTML(
                            webpageResp.session.request('GET',
                                                        webpageResp.url+'&'+pageq,
                                                        headers=webpageResp.request.headers),
                            jobKeyId,
                            pageKeyId,
                            False))
        return l
    
    def getJobLinksByJSON(self, **kwargs):
        pass

    def getJobDescByHTML(self,
        webpageResp:requests_html.HTMLResponse,
        descKey:str,
        **kwargs):
        return webpageResp.html.find(descKey)[0].text

    def getJobDescByJSON(self, **kwargs):
        pass

    ADDITIONS = {
        'request':request,
        'getJobLinksByHTML':getJobLinksByHTML,
        'getJobLinksByJSON':getJobLinksByJSON,
        'getJobDescByHTML':getJobDescByHTML,
        'getJobDescByJSON':getJobDescByJSON,
    }

    def addToPlan(self, add, **kwargs):
        if isinstance(add, Plan):
            self.plan.append(add)
        elif add in Plan.ADDITIONS:
            self.plan.append(partial(Plan.ADDITIONS[add], self, **kwargs))
        else:
            raise NotImplementedError('That action is not addable in Plan.')

    def executePlan(self, reqDict, **kwargs):
        self.session = get_legacy_session()
        x = reqDict
        for m in self.plan:
            if isinstance(m, Plan):
                x = m.executePlan(x, **kwargs)
            else:
                x = m(x, **kwargs)
        self.session = None
        return x