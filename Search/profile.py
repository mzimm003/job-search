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
            search:Search = Search(),
            ) -> None:
        self.name = name
        self.search : Search = search
        self.currentPosts : Dict[str,'Posting'] = {}
        self.historicalPosts : Dict[str,'Posting'] = {}

    @classmethod
    def bySearch(cls, search:Search):
        return cls(name=search.orgName, search=search)

    def defineSearch(self, search:Search):
        self.search = search
    
    def gatherPosts(self):
        self.currentPosts = {}
        jobs = self.search.listJobs()
        for job in jobs:
            if not job in self.historicalPosts:
                self.currentPosts[job] = Posting(job, self.search.getJobDesc(job))
        self.historicalPosts.update(self.currentPosts)
    
    def getSearch(self):
        return self.search

    def processPosts(self):
        for cp in self.currentPosts:
            pass


class Posting:
    def __init__(
            self,
            link:str,
            desc:str,
            ) -> None:
        self.link = link
        self.desc = desc
    
    @classmethod
    def byLink(cls, link):
        pass


    def getDesc(self):
        pass

    def process(self):
        pass

    def engageChatGPT(self):
        pass