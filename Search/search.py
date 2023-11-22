from typing import (
    Callable,
    List,
    Dict,
)
from functools import partial
from Search.utility import (
    request,
    getlinks,
    getDesc
)

class Search:
    def __init__(
            self,
            orgName:str = '',
            listJobsMethod:List[Callable] = [],
            getJobDescMethod:List[Callable] = [],
            searchReq:Dict = {},
            searchPhrases:List[str] = '',
            retType:str = 'json'
            ) -> None:
        self.orgName = orgName
        self.listJobsMethod = listJobsMethod
        self.getJobDescMethod = getJobDescMethod
        self.searchReq = searchReq
        self.searchPhrases = searchPhrases
        self.retType = retType
    
    def listJobs(self) -> List[str]:
        '''
        return ...string links?... to job postings
        '''
        jobs = []
        for srchPhrs in self.searchPhrases:
            
        return self.runMethod(self.listJobsMethod, self.searchReq)
    
    def getJobDesc(self, link) -> List[str]:
        reqDict = {
            'method':'GET',
            'url':link,
            'headers':'{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"}'
            }
        return self.runMethod(self.listJobsMethod, reqDict)

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

    @classmethod
    def byJSON(
        self,
        searchReq:Dict = {},
        ):
        return Search(
            [],
            searchReq,
            'json')
        

    @classmethod
    def byHTML(
        cls,
        searchReq:Dict = {},
        jobKeyId = '',
        descKey = '',
        ):
        obj = cls()
        orgName = searchReq['url'].lstrip('https://')
        obj.orgName = orgName[:orgName.find('/')]
        obj.listJobsMethod = [
            partial(request),
            partial(getlinks, keyword=jobKeyId),
            ]
        obj.searchReq = searchReq
        obj.getJobDescMethod = [
            partial(request),
            partial(getDesc, descKey=descKey)
            ]
        obj.retType = 'html'
        return obj
