from typing import (
    List,
)
from Search.search import Search


class Profile:
    def __init__(
            self,
            name:str,
            ) -> None:
        self.name = name
        self.searches : List[Search] = []
        self.currentPosts : List = None

    def addSearch(self, search:Search):
        self.searches.append(search)

    def populateSearches(self):
        #TODO
        x = None
        for i in x:
            self.incorporateSearch()
    
    def gatherPosts(self):
        self.currentPosts = []
        for s in self.searches:
            jobs = s.getJobList()
            for job in jobs:
                self.currentPosts.append(job)

    def processPosts(self):
        pass

class Posting:
    def __init__(
            self,
            link,
            ) -> None:
        self.link = link

    def getDesc(self):
        pass

    def engageChatGPT(self):
        pass