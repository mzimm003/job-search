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
        self.currentPosts = {}
        self.historicalPosts = {}
    
    def addProfile(self, prof:'Profile'):
        self.profiles[prof.name] = prof
    
    def getNewJobs(self):
        for n, p in self.profiles.items():
            p.gatherPosts()
            self.currentPosts.update(p.currentPosts)
            self.historicalPosts.update(p.historicalPosts)

    def getNewJobsByProfile(self, prof:'Profile'):
        prof.gatherPosts()
        self.currentPosts.update(prof.currentPosts)
        self.historicalPosts.update(prof.historicalPosts)

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
        self.ignorablePosts : Set[str] = set()
        self.jobCount = 0

    @classmethod
    def bySearch(cls, search:Search):
        return cls(name=search.orgName, search=search)

    def defineSearch(self, search:Search):
        self.search = search

    def samplePosts(self):
        jobs = self.search.listJobLinks()
        return self.search.getJobDesc(jobs[0])
    
    def gatherPosts(self):
        #################REDOOOING##################3
        self.currentPosts = {}
        jobs = self.search.listJobLinks()
        for job in jobs:
            if not job in self.ignorablePosts:
                post = Posting.bySearch(self.getSearch())
                relevantJob = False
                for phrs in self.search.searchPhrases:
                    if (post.getTitle().lower().find(phrs.lower()) != -1 or
                        post.getDesc().lower().find(phrs.lower()) != -1):
                        relevantJob = True
                        break
                if relevantJob:
                    self.currentPosts[self.name+'-'+str(self.jobCount)] = post
                    self.jobCount += 1
                self.ignorablePosts.add(job)
        self.historicalPosts.update(self.currentPosts)
    
    def getSearch(self):
        return self.search

    def processPosts(self):
        for cp in self.currentPosts:
            pass
    
    def CLEARALLPOSTS(self):
        self.currentPosts = {}
        self.historicalPosts = {}
        self.ignorablePosts = set()
        self.jobCount = 0


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
    def bySearch(cls, search:Search) -> 'Posting':
        pass

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

    def process(self):
        pass

    def engageChatGPT(self):
        pass