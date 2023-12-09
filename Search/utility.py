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
        self.plan = []

    @classmethod
    def peekLinks(cls, retType='html', renReq=False):
        p = cls()
        p.addToPlan('request')
        if renReq:
            p.addToPlan('renderRequest')

        if retType == 'html':
            p.addToPlan('getLinksByHTML')
        elif retType == 'json':
            p.addToPlan('getLinksByJSON')
            
        return p

    @classmethod
    def jobLinksByOptions(cls, retType='html'):
        p = cls()
        if retType == 'html':
            p.addToPlan('getJobLinksByHTML')
        elif retType == 'json':
            p.addToPlan('getJobLinksByJSON')
        
        return p
    
    @classmethod
    def requestByOptions(cls, renReq=False):
        p = cls()
        p.addToPlan('request')
        if renReq:
            p.addToPlan('renderRequest')
        
        return p
    
    @classmethod
    def jobDescByOptions(cls, retType='html', renReq=False):
        p = cls()
        p.addToPlan('request')
        if renReq:
            p.addToPlan('renderRequest')

        if retType == 'html':
            p.addToPlan('getJobDescByHTML')
        elif retType == 'json':
            p.addToPlan('getJobDescByJSON')
        
        return p
    
    @classmethod
    def jobTitleByOptions(cls, retType='html', renReq=False):
        p = cls()
        p.addToPlan('request')
        if renReq:
            p.addToPlan('renderRequest')

        if retType == 'html':
            p.addToPlan('getJobTitleByHTML')
        elif retType == 'json':
            p.addToPlan('getJobTitleByJSON')
        
        return p
    
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
    
    @classmethod
    def JSONJobLinksDefault(cls):
        p = cls()
        p.addToPlan('request')
        p.addToPlan('getJobLinksByJSON')
        return p
    
    @classmethod
    def JSONJobDescDefault(cls):
        p = cls()
        p.addToPlan('request')
        p.addToPlan('getJobDescByJSON')
        return p
    
    def request(self, reqDict:Dict, **kwargs):
        ses = get_legacy_session()
        return ses.request(**reqDict)
    
    def renderRequest(self, req, **kwargs):
        req.html.render()
        return req

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
    
    def getLinksByHTML(
            self,
            webpageResp:requests_html.HTMLResponse,
            **kwargs):
        l = [l for l in webpageResp.html.links]
        return l
    
    def getJobLinksByJSON(self,
                          webpageResp:requests_html.HTMLResponse,
                          jobListPathKeyIds:List[str],
                          jobLinkKeyId:List[str],
                          **kwargs):
        jobList = webpageResp.json()
        jobLinks = []
        for k in jobListPathKeyIds:
            jobList = jobList[k]
        for job in jobList:
            jobLinks.append(job[jobLinkKeyId])
        return jobLinks

    def getJobDescByHTML(self,
        webpageResp:requests_html.HTMLResponse,
        descKey:str,
        **kwargs):
        return webpageResp.html.find(descKey)[0].text
    
    def getJobTitleByHTML(self,
        webpageResp:requests_html.HTMLResponse,
        titleKey:str,
        **kwargs):
        return webpageResp.html.find(titleKey)[0].text

    def getJobDescByJSON(self, **kwargs):
        pass
    
    def getJobTitleByJSON(self, **kwargs):
        pass

    ADDITIONS = {
        'request':request,
        'renderRequest':renderRequest,
        'getLinksByHTML':getLinksByHTML,
        'getJobLinksByHTML':getJobLinksByHTML,
        'getJobLinksByJSON':getJobLinksByJSON,
        'getJobDescByHTML':getJobDescByHTML,
        'getJobDescByJSON':getJobDescByJSON,
        'getJobTitleByHTML':getJobTitleByHTML,
        'getJobTitleByJSON':getJobTitleByJSON,
    }

    def addToPlan(self, add, **kwargs):
        if isinstance(add, Plan):
            self.plan.append(add)
        elif add in Plan.ADDITIONS:
            self.plan.append(partial(Plan.ADDITIONS[add], self, **kwargs))
        else:
            raise NotImplementedError('That action is not addable in Plan.')
    
    def insertInPlan(self, add, idx, **kwargs):
        if isinstance(add, Plan):
            self.plan.insert(idx, add)
        elif add in Plan.ADDITIONS:
            self.plan.insert(idx, partial(Plan.ADDITIONS[add], self, **kwargs))
        else:
            raise NotImplementedError('That action is not addable in Plan.')


    def executePlan(self, initInp, **kwargs):
        x = initInp
        for m in self.plan:
            if isinstance(m, Plan):
                x = m.executePlan(x, **kwargs)
            else:
                x = m(x, **kwargs)
        return x