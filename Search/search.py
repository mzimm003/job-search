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
            findJobsMethod:Plan = None,
            viewJobMethod:List[Callable] = None,
            searchReq:Request = None,
            searchPhrases:List[str] = None,
            jobKeyId:str = '',
            pageKeyId:str = 'page',
            descKey:str = '',
            jobListPathKeyIds:str = '',
            jobLinkKeyId:str = '',
            jobListRetType:str = '',
            jobDescRetType:str = '',
            ) -> None:
        self.orgName = orgName
        self.findJobsMethod = Plan() if findJobsMethod is None else findJobsMethod
        self.viewJobMethod = [] if viewJobMethod is None else viewJobMethod
        self.searchReq = Request() if searchReq is None else searchReq
        self.searchPhrases = [] if searchPhrases is None else searchPhrases
        self.jobKeyId = jobKeyId
        self.pageKeyId = pageKeyId
        self.descKey = descKey
        self.jobListPathKeyIds = jobListPathKeyIds
        self.jobLinkKeyId = jobLinkKeyId
        self.jobListRetType = jobListRetType
        self.jobDescRetType = jobDescRetType
    
    def updatePlan(self, plan:Plan, planStr:str):
        if planStr == 'listJobs':
            self.findJobsMethod = plan
        elif planStr == 'jobDesc':
            self.viewJobMethod = plan

    def listJobLinks(self) -> List[str]:
        '''
        return ...string links?... to job postings
        '''
        jobs = set()
        for srchPhrs in self.searchPhrases:
            reqDict = self.searchReq.getRequestDict(srchPhrs)
            wp = self.findJobsMethod.executePlan(reqDict, **self.__dict__)
            
            jobs.update()
        return list(jobs)
    
    def getJobDesc(self, link) -> List[str]:
        reqDict = {
            'method':'GET',
            'url':link,
            'headers':{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}
            }
        return self.viewJobMethod.executePlan(reqDict, **self.__dict__)

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
        obj.findJobsMethod = Plan.requestByOptions(renReq=jobListRenReq)
        obj.searchReq = searchReq
        obj.descKey = descKey
        obj.viewJobMethod = Plan.requestByOptions(renReq=jobDescRenReq)
        obj.jobListRetType = jobListRetType
        obj.jobDescRetType = jobDescRetType
        return obj