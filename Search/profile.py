from typing import (
    List,
    Dict,
    Set
)
from Search.search import Search
import enum

class Portfolio:
    def __init__(self) -> None:
        self.profiles:Dict[str, 'Profile'] = {}
        self.currentPosts:Dict[str, Dict] = {}
        self.historicalPosts:Dict[str, Dict] = {}
    
    def addProfile(self, prof:'Profile'):
        self.profiles[prof.name] = prof
    
    def getNewJobs(self):
        for n, p in self.profiles.items():
            self.getNewJobsByProfile(p)

    def getNewJobsByProfile(self, prof:'Profile'):
        prof.gatherPosts()
        if not prof.name in self.currentPosts:
            self.currentPosts[prof.name] = {}
        if not prof.name in self.historicalPosts:
            self.historicalPosts[prof.name] = {}
        self.currentPosts[prof.name].update(prof.currentPosts)
        self.historicalPosts[prof.name].update(prof.historicalPosts)

    def CLEARALLPOSTS(self):
        for k, p in self.profiles.items():
            p.CLEARALLPOSTS()
        self.currentPosts = {}
        self.historicalPosts = {}
        

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
        self.jobCount = 0

    @classmethod
    def bySearch(cls, search:Search):
        return cls(name=search.orgName, search=search)

    def defineSearch(self, search:Search):
        self.search = search

    def samplePosts(self):
        jobs = self.search.listJobLinks(sample=True)
        sampleJobSearchDesc = self.search.getFullDescriptionsByLinks(jobs[0])[0]
        post = Posting.bySearchDesc(sampleJobSearchDesc)
        return post.displayDescription()
    
    def gatherPosts(self):
        self.currentPosts = {}
        jobs = self.search.getJobDescs()
        for job in jobs:
            post = Posting.bySearchDesc(job)
            relevantJob = False
            for phrs in self.search.searchPhrases:
                if (post.getTitle().lower().find(phrs.lower()) != -1 or
                    post.getDesc().lower().find(phrs.lower()) != -1):
                    relevantJob = True
                    break
            if relevantJob:
                self.currentPosts[post.getTitle()+'-'+str(self.jobCount)] = post
                self.jobCount += 1
        self.historicalPosts.update(self.currentPosts)
    
    def getSearch(self):
        return self.search

    def processPosts(self):
        for cp in self.currentPosts:
            pass
    
    def CLEARALLPOSTS(self):
        self.currentPosts = {}
        self.historicalPosts = {}
        self.jobCount = 0
        self.search.CLEARALLPOSTS()


class Posting:
    class STATUS(enum.Enum):
        Pending = enum.auto()
        Applied = enum.auto()
        Ignored = enum.auto()

    def __init__(
            self,
            link:str,
            title:str,
            desc:str,
            ) -> None:
        self.link = link
        self.title = title
        self.desc = desc
        self.status = Posting.STATUS.Pending
    
    @classmethod
    def bySearchDesc(cls, searchDesc:Dict) -> 'Posting':
        return cls(**searchDesc)

    def getStatus(self):
        return self.status.name
    
    def toggleApplied(self):
        if self.status == Posting.STATUS.Applied:
            self.status = Posting.STATUS.Pending
        else:
            self.status = Posting.STATUS.Applied
    
    def toggleIgnore(self):
        if self.status == Posting.STATUS.Ignored:
            self.status = Posting.STATUS.Pending
        else:
            self.status = Posting.STATUS.Ignored

    def getDesc(self):
        return self.desc
    
    def getTitle(self):
        return self.title
    
    def displayDescription(self):
        return self.getTitle() + '\n' + self.getDesc()

    def process(self):
        pass

    def engageChatGPT(self):
        pass