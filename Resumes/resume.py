from typing import (
    List,
    Union,
)
import enum
import datetime

class ResumeRevision:
    def __init__(
            self,
            resume = None,
            keepDict = None,
            revisionDict = None,
            ):
        self.resume = resume
        self.keepDict = {} if keepDict is None else keepDict
        self.guiKeepMap = {}
        self.revisionDict = {} if revisionDict is None else revisionDict
        self.guiRevisionMap = {}

    @classmethod
    def fromResume(cls, resume:'Resume'):
        # keepDict = {}
        # for sec in resume.getSections():
        #     keepDict[sec.getTitle()] = {}
        #     for subsec in sec.getContent():
        #         elms = subsec.getElements()
        #         if isinstance(elms[0],str):
        #             keepDict[sec.getTitle()][subsec.getSubject()] = [True for e in elms]
        #         else:
        #             keepDict[sec.getTitle()][subsec.getSubject()] = {}
        #             for subsubsec in elms:
        #                 keepDict[sec.getTitle()][subsec.getSubject()][subsubsec.getSubject()] = [True for e in subsubsec.getElements()]

        revisionDict = {}
        for sec in resume.getSections():
            # revisionDict[sec.getTitle()] = {}
            for subsec in sec.getContent():
                elms = subsec.getElements()
                if isinstance(elms[0],str):
                    revisionDict.update({id(e):{"Revision":e,"Keep":True} for e in elms})
                else:
                    # revisionDict[sec.getTitle()][subsec.getSubject()] = {}
                    for subsubsec in elms:
                        revisionDict.update({id(e):{"Revision":e,"Keep":True} for e in subsubsec.getElements()})
        return cls(resume, revisionDict=revisionDict)

    def getValueByID(self, id, val="Revision"):
        return self.revisionDict[id][val]

    def markKeep(self, key=None, id=None, mark=True):
        if key:
            self.revisionDict[self.guiRevisionMap[key]]["Keep"] = mark
        else:
            self.revisionDict[id]["Keep"] = mark

    def setRevision(self, key=None, id=None, revision=''):
        if key:
            self.revisionDict[self.guiRevisionMap[key]]["Revision"] = revision
        else:
            self.revisionDict[id]["Revision"] = revision


    def generateResume(self):
        pass

    def addMapping(self, key, id):
        self.guiRevisionMap[key] = id
    
    def resetMappings(self):
        self.guiRevisionMap = {}

class Resume:
    def __init__(
            self,
            org:str = None,
            job:str = None,
            name:str = None,
            email:str = None,
            phone:str = None,
            location:str = None,
            linkedInLink:str = None,
            gitHubLink:str = None,
            sections:List['Section'] = None,
            ):
        self.org:str = '' if org is None else org
        self.job:str = '' if job is None else job
        self.name:str = '' if name is None else name
        self.email:str = '' if email is None else email
        self.phone:str = '' if phone is None else phone
        self.location:str = '' if location is None else location
        self.linkedInLink:str = '' if linkedInLink is None else linkedInLink
        self.gitHubLink:str = '' if gitHubLink is None else gitHubLink
        self.sections:List[Section] = [] if sections is None else sections

    def addSection(self, section:'Section'):
        self.sections.append(section)

    def getSections(self)->List['Section']:
        return self.sections
    
    # def asDict(self, bulletsOnly=True, skillCSVsOnly=False, skipEdu=False):
    #     s = self.__stringList(bulletsOnly, skillCSVsOnly, skipEdu)

    def asString(self, bulletsOnly=False, skillCSVsOnly=False, skipEdu=False, lineNums=False, asDict=False):
        s = self.__stringList(bulletsOnly, skillCSVsOnly, skipEdu)

        if asDict:
            d = {}
            for i, l in enumerate(s):
                d[i] = l.strip('\t')
            return d
        
        if lineNums:
            temp = []
            for i, l in enumerate(s):
                temp.append(str(i)+' '+l)
            s = temp
        return '\n'.join(s)

    def __stringList(self, bulletsOnly=False, skillCSVsOnly=False, skipEdu=False):
        s = []
        if not bulletsOnly and not skillCSVsOnly:
            s.append(self.name)
        for sec in self.sections:
            if not (skipEdu and sec.title=="Education"):
                if not bulletsOnly and not skillCSVsOnly:
                    s.append(sec.title+":")
                for con in sec.content:
                    if not bulletsOnly and not skillCSVsOnly:
                        s.append('\t'+con.subject)
                    csv = []
                    for elm in con.elements:
                        if isinstance(elm, str):
                            if con.type == Subsection.Types.SKILL:
                                csv.append(elm)
                            else:
                                if not skillCSVsOnly:
                                    s.append('\t\t-'+elm)
                        else:
                            if elm.type == Subsection.Types.PROJECT or elm.type == Subsection.Types.POSITION:
                                if not bulletsOnly and not skillCSVsOnly:
                                    s.append('\t\t'+elm.subject)
                                for e in elm.elements:
                                    if not skillCSVsOnly:
                                        s.append('\t\t\t-'+e)
                            elif elm.type == Subsection.Types.SKILL:
                                if not bulletsOnly:
                                    s.append('\t\t'+elm.subject+', '+', '.join([e for e in elm.elements]))
                    if csv:
                        if not bulletsOnly:
                            s.append('\t\t'+', '.join(csv))
        return s


class Section:
    def __init__(
            self,
            title = None,
            content = None,
            ) -> None:
        self.title:str = '' if title is None else title
        self.content:List[Subsection] = [] if content is None else content

    def getTitle(self):
        return self.title
    
    def getContent(self)->List['Subsection']:
        return self.content

    def addSubSection(self, subsection:'Subsection'):
        self.content.append(subsection)

    @classmethod
    def fromOldSection(cls, **kwargs):
        return cls(**kwargs)

class Subsection:
    class Types(enum.Enum):
        ORGANIZATION = enum.auto()
        SCHOOL = enum.auto()
        SKILL = enum.auto()
        PROJECT = enum.auto()
        POSITION = enum.auto()
    def __init__(
            self,
            subject = None,
            startDate = None,
            endDate = None,
            location = None,
            elements = None,
            type = None,
            ) -> None:
        self.subject:str = '' if subject is None else subject
        self.startDate:datetime.date = startDate
        self.endDate:datetime.date = endDate
        self.location:str = '' if location is None else location
        self.elements:List[Subsection]|List[str] = [] if elements is None else elements
        self.type:Subsection.Types = Subsection.Types.ORGANIZATION if type is None else type
    
    def getType(self):
        return self.type
    
    def getSubject(self):
        return self.subject
    
    def getElements(self):
        return self.elements

    def addSubSection(self, subsection:'Subsection'):
        self.elements.append(subsection)