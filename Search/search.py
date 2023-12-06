from typing import (
    Callable,
    List,
    Dict,
)
from functools import partial
from Search.utility import (
    Plan,
)
from Search.transforms import Transform, Request

class Search:
    def __init__(
            self,
            orgName:str = '',
            listJobsMethod:Plan = None,
            getJobDescMethod:List[Callable] = None,
            searchReq:Request = None,
            searchPhrases:List[str] = None,
            jobKeyId:str = '',
            pageKeyId:str = 'page',
            descKey:str = '',
            jobListPathKeyIds:str = '',
            jobLinkKeyId:str = '',
            ) -> None:
        self.orgName = orgName
        self.listJobsMethod = Plan() if listJobsMethod is None else listJobsMethod
        self.getJobDescMethod = [] if getJobDescMethod is None else getJobDescMethod
        self.searchReq = Request() if searchReq is None else searchReq
        self.searchPhrases = [] if searchPhrases is None else searchPhrases
        self.jobKeyId = jobKeyId
        self.pageKeyId = pageKeyId
        self.descKey = descKey
        self.jobListPathKeyIds = jobListPathKeyIds
        self.jobLinkKeyId = jobLinkKeyId
    
    def updatePlan(self, plan:Plan, planStr:str):
        if planStr == 'listJobs':
            self.listJobsMethod = plan
        elif planStr == 'jobDesc':
            self.getJobDescMethod = plan

    def listJobs(self) -> List[str]:
        '''
        return ...string links?... to job postings
        '''
        jobs = set()
        for srchPhrs in self.searchPhrases:
            reqDict = self.searchReq.getRequestDict(srchPhrs)
            jobs.update(self.listJobsMethod.executePlan(reqDict, **self.__dict__))
        return list(jobs)
    
    def getJobDesc(self, link) -> List[str]:
        reqDict = {
            'method':'GET',
            'url':link,
            'headers':{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
            }
        return self.getJobDescMethod.executePlan(reqDict, **self.__dict__)

    def runMethod(self, method, reqDict):
        x = None
        for i, m in enumerate(method):
            if i == 0:
                x = m(reqDict)
            else:
                x = m(x)
        return x

    def addSearchPhrase(self, phrase):
        self.searchPhrases.append(phrase)
    
    def setJobKeyId(self, key:str):
        self.jobKeyId = key
        # for f in self.listJobsMethod:
        #     if 'jobKeyword' in f.keywords:
        #         f.keywords['jobKeyword'] = key

    def setPageKeyId(self, key:str):
        self.pageKeyId = key
        # for f in self.listJobsMethod:
        #     if 'pageKeyword' in f.keywords:
        #         f.keywords['pageKeyword'] = key

    def setDescKey(self, key:str):
        self.descKey = key
        # for f in self.getJobDescMethod:
        #     if 'keyword' in f.keywords:
        #         f.keywords['keyword'] = key

    def setSearchPhrases(self, phrases:List[str]):
        self.searchPhrases = phrases

    @classmethod
    def byOptions(
        cls,
        searchReq:Request,
        jobKeyId = '',
        pageKeyId = 'page',
        descKey = '',
        jobListRetType = 'html',
        jobListRenReq = False,
        jobDescRetType = 'html',
        jobDescRenReq = False,
        ):
        obj = cls()
        obj.orgName = searchReq.getOrg()
        obj.jobKeyId = jobKeyId
        obj.pageKeyId = pageKeyId
        obj.listJobsMethod = Plan.jobLinksByOptions(retType=jobListRetType,renReq=jobListRenReq)
        obj.searchReq = searchReq
        obj.descKey = descKey
        obj.getJobDescMethod = Plan.jobDescByOptions(retType=jobDescRetType,renReq=jobDescRenReq)
        return obj
    

    @classmethod
    def byHTML(
        cls,
        searchReq:Request,
        jobKeyId = '',
        pageKeyId = 'page',
        descKey = '',
        ):
        obj = cls()
        obj.orgName = searchReq.getOrg()
        obj.jobKeyId = jobKeyId
        obj.pageKeyId = pageKeyId
        obj.listJobsMethod = Plan.HTMLJobLinksDefault()
        obj.searchReq = searchReq
        obj.descKey = descKey
        obj.getJobDescMethod = Plan.HTMLJobDescDefault()
        obj.retType = 'html'
        return obj
    
    @classmethod
    def byJSON(
        cls,
        searchReq:Request,
        jobKeyId = '',
        pageKeyId = 'page',
        descKey = '',
        ):
        obj = cls()
        obj.orgName = searchReq.getOrg()
        obj.pageKeyId = pageKeyId
        obj.jobListPathKeyIds, obj.jobLinkKeyId = jobKeyId.split(';')
        obj.jobLinkKeyId = obj.jobLinkKeyId.strip()
        obj.jobListPathKeyIds = [x.strip() for x in obj.jobListPathKeyIds.split(',')]
        obj.listJobsMethod = Plan.JSONJobLinksDefault()
        obj.searchReq = searchReq
        obj.descKey = descKey
        obj.getJobDescMethod = Plan.HTMLJobDescDefault()
        obj.retType = 'json'
        return obj
