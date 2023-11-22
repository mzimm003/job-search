from typing import (
    List,
    Dict
)
from Search.search import Search

class Portfolio:
    def __init__(self) -> None:
        self.profiles:Dict[str, Profile] = {}
        self.currentPosts = {}
        self.historicalPosts = {}
    
    def addProfile(self, prof:'Profile'):
        self.profiles[prof.name] = prof
    
    def getNewJobs(self):
        for n, p in self.profiles.items():
            p.gatherPosts()
            #TODO

class Profile:
    def __init__(
            self,
            name:str,
            searches:List[Search] = [],
            ) -> None:
        self.name = name
        self.searches : List[Search] = searches
        self.currentPosts : Dict[str,'Posting'] = {}
        self.historicalPosts : Dict[str,'Posting'] = {}

    @classmethod
    def bySearch(cls, search:Search):
        return cls(name=search.orgName, searches=search)

    def addSearch(self, search:Search):
        self.searches.append(search)
    
    def gatherPosts(self):
        self.currentPosts = []
        for s in self.searches:
            jobs = s.getJobList()
            for job in jobs:
                self.currentPosts[job] = Posting.byLink(job)
    
    def getSearches(self):
        return self.searches

    def processPosts(self):
        for cp in self.currentPosts:
            pass


class Posting:
    def __init__(
            self,
            link,
            ) -> None:
        self.link = link
    
    @classmethod
    def byLink(cls, link):
        pass


    def getDesc(self):
        pass

    def process(self):
        pass

    def engageChatGPT(self):
        pass