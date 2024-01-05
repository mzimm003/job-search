from typing import (
    Callable,
    List,
    Dict,
    Set,
)
from functools import partial
from Search.utility import (
    Plan,
)
from Search.transforms import Transform, Request
from requests_html import (
    HTMLSession
)
from typing import (
    Dict,
    List,
    Callable
)
from enum import Enum
import requests_html

import urllib.parse
import urllib3
import ssl
from contextlib import contextmanager
import asyncio

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

class Search:
    def __init__(
            self,
            orgName:str = None,
            searchReq:Request = None,
            searchPhrases:List[str] = None,
            jobKeyId:str = None,
            pageKeyId:str = None,
            titleKey:str = None,
            descKey:str = None,
            jobListPathKeyIds:str = None,
            jobListRetType:str = None,
            jobDescRetType:str = None,
            listRenReq:bool = None,
            descRenReq:bool = None,
            ) -> None:
        self.orgName = '' if orgName is None else orgName
        self.searchReq = Request() if searchReq is None else searchReq
        self.searchPhrases = [] if searchPhrases is None else searchPhrases
        self.jobKeyId = 'jobs' if jobKeyId is None else jobKeyId
        self.pageKeyId = 'page' if pageKeyId is None else pageKeyId
        self.titleKey = 'type.class; e.g. div.main' if titleKey is None else titleKey
        self.descKey = 'type.class; e.g. div.main' if descKey is None else descKey
        self.jobListPathKeyIds = [] if jobListPathKeyIds is None else jobListPathKeyIds
        self.jobListRetType = 'html' if jobListRetType is None else jobListRetType
        self.jobDescRetType = 'html' if jobDescRetType is None else jobDescRetType
        self.listRenReq = False if listRenReq is None else listRenReq
        self.descRenReq = False if descRenReq is None else descRenReq
        self.ses = None
        self.ignorablePosts : Set[str] = set()

    @contextmanager
    def __engageSession(self):
        self.ses = get_legacy_session()
        try:
            yield self.ses
        finally:
            self.ses = None

    def __request(self, reqDict:Dict, renReq:bool=False):
        req = self.ses.request(**reqDict)
        if renReq:
            # asyncio.set_event_loop(asyncio.new_event_loop())
            req.html.render()
        return req

    def CLEARALLPOSTS(self):
        self.ignorablePosts = set()

    def getJobDescs(
            self,):
        links = self.listJobLinks()
        relevantLinks = [l for l in links if not l in self.ignorablePosts]
        self.ignorablePosts.update(links)
        return self.getFullDescriptionsByLinks(relevantLinks)

    def listJobLinks(self, sample=False) -> List[str]:
        '''
        return ...string links?... to job postings
        '''
        jobs = set()
        for srchPhrs in self.searchPhrases:
            reqDict = self.searchReq.getRequestDict(srchPhrs)
            links = self.getJobLinksByRequestDict(reqDict)
            jobs.update(links)
            if sample and jobs:
                break
        return list(jobs)

    def getJobLinksByRequestDict(
            self,
            reqDict:Dict,
            followPages:bool=True):
        l = []
        with self.__engageSession():
            wp = self.__request(reqDict, self.listRenReq)
            if self.jobListRetType == 'html':
                for link in wp.html.absolute_links:
                    if self.jobKeyId in link:
                        l.append(link)
                    if followPages and self.pageKeyId in link:
                        pageq = urllib.parse.urlparse(link).query
                        l.extend(self.getJobLinksByRequestDict(
                            {'method':'GET',
                             'url':wp.url+'&'+pageq,
                             'headers':wp.request.headers},
                             False))
            elif self.jobListRetType == 'json':
                jobList = wp.json()
                for k in self.jobListPathKeyIds:
                    if isinstance(jobList, list):
                        k = int(k)
                    jobList = jobList[k]
                for job in jobList:
                    l.append(job[self.jobKeyId])
        return l
    
    def peekLinks(
            self,
            reqDict:Dict,
            ):
        l = None
        with self.__engageSession():
            wp = self.__request(reqDict, self.listRenReq)
            if self.jobListRetType == 'html':
                l = [l for l in wp.html.links]
            elif self.jobListRetType == 'json':
                l = wp.json()
        return l

    def __getJobInfoByHTML(self,
        wpResp:requests_html.HTMLResponse,
        key:str):
        return wpResp.html.find(key)[0].text
    
    def __getJobInfoByJSON(self,
        wpResp:requests_html.HTMLResponse,
        key:str):
        raise NotImplementedError

    def __getFullDesc(self,
        wpResp:requests_html.HTMLResponse):
        fullDesc = {
            'title':self.__getJobInfoByHTML(wpResp, self.titleKey),
            'desc':self.__getJobInfoByHTML(wpResp, self.descKey),
            } if self.jobDescRetType else {
            'title':self.__getJobInfoByJSON(wpResp, self.titleKey),
            'desc':self.__getJobInfoByJSON(wpResp, self.descKey),
            }
        return fullDesc

    def getFullDescriptionsByLinks(
            self,
            links:List[str],
            ):
        if isinstance(links, str):
            links = [links]
        descs = []
        with self.__engageSession():
            for link in links:
                reqDict = {
                    'method':'GET',
                    'url':link,
                    'headers':{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
                    }
                wp = self.__request(reqDict, self.descRenReq)
                descDict = {'link':link}
                descDict.update(self.__getFullDesc(wp))
                descs.append(descDict)
        return descs

    def addSearchPhrase(self, phrase):
        self.searchPhrases.append(phrase)
    
    def setJobKeyId(self, key:str):
        self.jobKeyId = key
        if self.jobListRetType == 'json':
            self.jobKeyId, jobListPathKeyIds = self.jobKeyId.split(';') if ';' in self.jobKeyId else (self.jobKeyId, '')
            self.jobListPathKeyIds = jobListPathKeyIds.split(',') if ',' in self.jobListPathKeyIds else []
    
    def getJobKeyId(self):
        ret = self.jobKeyId
        if self.jobListRetType == 'json' and self.jobListPathKeyIds:
            ret += ';'+','.join(self.jobListPathKeyIds)
        return ret

    def setPageKeyId(self, key:str):
        self.pageKeyId = key
    
    def getPageKeyId(self):
        return self.pageKeyId

    def setDescKey(self, key:str):
        self.descKey = key

    def getDescKey(self):
        return self.descKey

    def setTitleKey(self, key:str):
        self.titleKey = key

    def getTitleKey(self):
        return self.titleKey
    
    def getSearchPhrases(self, asString=False):
        if asString:
            return '\n'.join(self.searchPhrases)
        return self.searchPhrases
    
    def getJobDescRetType(self):
        return self.jobDescRetType
    
    def setJobDescRetType(self, typ):
        self.jobDescRetType = typ
    
    def getJobListRetType(self):
        return self.jobListRetType
    
    def setJobListRetType(self, typ):
        self.jobListRetType = typ
    
    def getListRenReq(self):
        return self.listRenReq
    
    def setListRenReq(self, req):
        self.listRenReq = req
    
    def getDescRenReq(self):
        return self.descRenReq
    
    def setDescRenReq(self, req):
        self.descRenReq = req

    def setSearchPhrases(self, phrases:List[str]):
        self.searchPhrases = phrases

    @classmethod
    def bySearchRequest(
        cls,
        searchReq:Request,
        orgName = None,
        jobKeyId = None,
        pageKeyId = None,
        titleKey = None,
        descKey = None,
        jobListRetType = None,
        jobDescRetType = None,
        listRenReq = False,
        descRenReq = False,
        ):
        creationDict = dict(
            orgName = searchReq.getOrg() if orgName is None else orgName,
            searchReq = searchReq,
            jobKeyId = jobKeyId,
            pageKeyId = pageKeyId,
            titleKey = titleKey,
            descKey = descKey,
            jobListRetType = jobListRetType,
            jobDescRetType = jobDescRetType,
            listRenReq = listRenReq,
            descRenReq = descRenReq,)
        
        if ';' in jobKeyId:
            jobKeyId, jobListPathKeyIds = jobKeyId.split(';')
            jobListPathKeyIds = jobListPathKeyIds.split(',')
            creationDict['jobKeyId'] = jobKeyId
            creationDict['jobListPathKeyIds'] = jobListPathKeyIds

        return cls(**creationDict)