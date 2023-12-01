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

class Plan:
    def __init__(self) -> None:
        self.session = None
        self.plan = []

    @classmethod
    def HTMLDefault(cls):
        p = cls()
        p.estSession()
        p.addToPlan('request')
        p.addToPlan('accessInstAttr', attr='html')
        p.addToPlan('accessInstAttr', attr='absolute_links')
        p.addToPlan('request')
        return p

    def estSession(self):
        self.session = get_legacy_session()
    
    def buildArgs(self, inp):
        x = inp
        args = []
        for m in self.plan:
            if isinstance(m, Plan):
                x = m.executePlan(x)
            else:
                x = m(x)
            args.append(x)
        return args
    
    def request(self, searchReq:Dict):
        return self.session.request(**searchReq)
    
    # def getHTMLLinks(self, html:requests_html.HTMLResponse):
    def accessInstAttr(self, inst, attr):
        return getattr(inst, attr)
    
    def extendByResult(self, l1:List, l2:List):
        l1.extend(l2)
        return l1

    def itrList(self, it:List, call:Callable):
        l = []
        for i in it:
            l.append(call(i))
        return l

    def itrDict(self, it:Dict, call:Callable):
        l = []
        for k, v in it.items():
            l.append(call(v))
        return l

    def getDictElement(self, d:Dict, key):
        return d[key]
    
    ADDITIONS = {
        'request':request,
        'itrList':itrList,
        'itrDict':itrDict,
        'getDictElement':getDictElement,
    }

    def addToPlan(self, add, **kwargs):
        if isinstance(add, Plan):
            self.plan.append(add)
        elif add in Plan.ADDITIONS:
            self.plan.append(partial(Plan.ADDITIONS[add], self, **kwargs))
        else:
            raise NotImplementedError('That action is not addable in Plan.')

    def executePlan(self, inp):
        x = inp
        for m in self.plan:
            if isinstance(m, Plan):
                x = m.executePlan(x)
            else:
                x = m(x)
        return x