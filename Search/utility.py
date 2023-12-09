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
from contextlib import contextmanager

'''Generously provided by:
https://stackoverflow.com/questions/71603314/ssl-error-unsafe-legacy-renegotiation-disabled
To address dated server side SSL (e.g. governmentjobs.com).
WARNING: Legacy server connection leaves possibility of MITM attack described here:
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
    def __init__(
            self,
            retType = None,
            renReq = None,
            jobKeyId = None,
            pageKeyId = None,
            jobListPathKeyIds = None,
            jobLinkKeyId = None,
            descKey = None,
            titleKey = None,) -> None:
        self.retType = '' if retType is None else retType
        self.renReq = False if renReq is None else renReq
        self.jobKeyId = '' if jobKeyId is None else jobKeyId
        self.pageKeyId = '' if pageKeyId is None else pageKeyId
        self.jobListPathKeyIds = [] if jobListPathKeyIds is None else jobListPathKeyIds
        self.jobLinkKeyId = '' if jobLinkKeyId is None else jobLinkKeyId
        self.descKey = '' if descKey is None else descKey
        self.titleKey = '' if titleKey is None else titleKey
        self.ses = None

    @contextmanager
    def __engageSession(self):
        self.ses = get_legacy_session()
        try:
            yield self.ses
        finally:
            self.ses = None

    def __request(self, reqDict:Dict):
        req = self.ses.request(**reqDict)
        if self.renReq:
            req.html.render()
        return req

    def getJobLinks(
            self,
            reqDict:Dict,
            followPages:bool=True):
        l = []
        with self.__engageSession():
            wp = self.__request(reqDict)
            if self.retType == 'html':
                for link in wp.html.absolute_links:
                    if self.jobKeyId in link:
                        l.append(link)
                    if followPages and self.pageKeyId in link:
                        pageq = urllib.parse.urlparse(link).query
                        l.extend(self.getJobLinks(
                                    self.__request({'method':'GET',
                                                    'url':wp.url+'&'+pageq,
                                                    'headers':wp.request.headers}),
                                    False))
            elif self.retType == 'json':
                jobList = wp.json()
                jobLinks = []
                for k in self.jobListPathKeyIds:
                    jobList = jobList[k]
                for job in jobList:
                    jobLinks.append(job[self.jobLinkKeyId])
        return l
    
    def peekLinks(
            self,
            reqDict:Dict,
            ):
        l = None
        with self.__engageSession():
            wp = self.__request(reqDict)
            if self.retType == 'html':
                l = [l for l in wp.html.links]
            elif self.retType == 'json':
                pass
        return l

    def __getJobDescByHTML(self,
        wpResp:requests_html.HTMLResponse):
        return wpResp.html.find(self.descKey)[0].text
    
    def __getJobTitleByHTML(self,
        wpResp:requests_html.HTMLResponse):
        return wpResp.html.find(self.titleKey)[0].text

    def __getFullDescByHTML(self,
        wpResp:requests_html.HTMLResponse):
        return {
            'title':self.__getJobTitleByHTML(wpResp),
            'desc':self.__getJobDescByHTML(wpResp)
        }

    def getFullDescriptions(
            self,
            links:List[str],
            ):
        if isinstance(link, str):
            links = [links]
        descs = []
        with self.__engageSession():
            for link in links:
                reqDict = {
                    'method':'GET',
                    'url':link,
                    'headers':{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
                    }
                wp = self.__request(reqDict)
                descDict = {'link':link}
                descDict.update(self.__getFullDescByHTML(wp))
                descs.append(descDict)
        return descs