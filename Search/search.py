from typing import (
    Callable,
    List,
    Dict,
)
from functools import partial
from Search.utility import (
    request,
    getlinks
)

class Search:
    def __init__(
            self,
            orgName:str = '',
            method:List[Callable] = [],
            searchReq:Dict = {},
            retType:str = 'json'
            ) -> None:
        self.orgName = orgName
        self.method = method
        self.searchReq = searchReq
        self.retType = retType
    
    def getJobList(self) -> List[str]:
        '''
        return ...string links?... to job postings
        '''
        return self.runMethod()

    def runMethod(self):
        x = None
        for i, m in enumerate(self.method):
            if i == 0:
                x = m()
            else:
                x = m(x)
        return x

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
        ):
        obj = cls()
        orgName = searchReq['url'].lstrip('https://')
        obj.orgName = orgName[:orgName.find('/')]
        obj.method = [
                partial(request, searchReq=searchReq),
                partial(getlinks, keyword=jobKeyId),
            ]
        # obj.searchReq = searchReq
        obj.retType = 'html'
        return obj
