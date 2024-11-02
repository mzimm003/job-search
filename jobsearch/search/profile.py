from typing import (
    List,
    Dict,
)
from jobsearch.search.search import Search
import enum
import datetime

class Portfolio:
    def __init__(self) -> None:
        self.profiles:Dict[str,'Profile'] = {}
    
    def addProfile(self, prof:'Profile'):
        self.profiles[prof.getName()] = prof

    def getProfiles(self):
        return self.profiles
    
    def getCurrentPosts(self):
        return {n:p.getCurrentPosts() for n,p in self.getProfiles().items()}
    
    def getHistoricalPosts(self):
        return {n:p.getHistoricalPosts() for n,p in self.getProfiles().items()}
        
    def getProfileNames(self):
        return list(self.getProfiles().keys())
    
    def selectProfileByName(self, name):
        return self.getProfiles()[name]
    
    def getNewJobs(self):
        for p in self.getProfiles().values():
            p.gatherPosts()

    def CLEARALLPOSTS(self):
        for p in self.getProfiles().values():
            p.CLEARALLPOSTS()

    def renameProfile(self, prof:'Profile', name:str):
        del self.profiles[prof.name]
        prof.setName(name)
        self.profiles[name] = prof

        
class Profile:
    NEWPROFILE = "--New--"
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
    
    @classmethod
    def default(cls):
        return cls(name=Profile.NEWPROFILE, search=Search())

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
    
    def getName(self):
        return self.name
    
    def setName(self, name:str):
        self.name = name
    
    def getSearch(self):
        return self.search
    
    def getCurrentPosts(self):
        return self.currentPosts
    
    def getHistoricalPosts(self):
        return self.historicalPosts
    
    def getLastApplied(self):
        date = None
        for post in self.getHistoricalPosts().values():
            if (date is None or
                (not post.getDateApplied() is None and
                date < post.getDateApplied())):
                date = post.getDateApplied()
        return date
    
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
        self.date_pulled = datetime.date.today()
        self.date_applied = None
    
    @classmethod
    def bySearchDesc(cls, searchDesc:Dict) -> 'Posting':
        return cls(**searchDesc)
    
    def getLink(self):
        return self.link

    def getStatus(self):
        return self.status.name
    
    def toggleApplied(self):
        if self.status == Posting.STATUS.Applied:
            self.status = Posting.STATUS.Pending
            self.date_applied = None
        else:
            self.status = Posting.STATUS.Applied
            self.date_applied = datetime.date.today()
        return self.status.name
    
    def toggleIgnore(self):
        if self.status == Posting.STATUS.Ignored:
            self.status = Posting.STATUS.Pending
        else:
            self.status = Posting.STATUS.Ignored
        self.date_applied = None
        return self.status.name

    def getDesc(self):
        return self.desc
    
    def getTitle(self):
        return self.title
    
    def getDatePulled(self):
        return self.date_pulled
    
    def getDateApplied(self):
        return self.date_applied

    def displayDescription(self):
        return self.getTitle() + '\n' + self.getDesc()

    def process(self):
        pass

    def engageChatGPT(self):
        pass