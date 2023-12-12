from typing import (
    List,
    Union,
)
import enum
import datetime
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
    
    def asString(self):
        s = []
        s.append(self.name)
        for sec in self.sections:
            s.append(sec.title+":")
            for con in sec.content:
                s.append('\t'+con.subject)
                csv = []
                for elm in con.elements:
                    if isinstance(elm, str):
                        if con.type == Subsection.Types.SKILL:
                            csv.append(elm)
                        else:
                            s.append('\t\t-'+elm)
                    else:
                        if elm.type == Subsection.Types.PROJECT or elm.type == Subsection.Types.POSITION:
                            s.append('\t\t'+elm.subject)
                            for e in elm.elements:
                                s.append('\t\t\t-'+e)
                        elif elm.type == Subsection.Types.SKILL:
                            s.append('\t\t'+elm.subject+', '+', '.join([e for e in elm.elements]))
                if csv:
                    s.append('\t\t'+', '.join(csv))
        return '\n'.join(s)

class Section:
    def __init__(
            self,
            title = None,
            content = None,
            ) -> None:
        self.title:str = '' if title is None else title
        self.content:List[Subsection] = [] if content is None else content
    
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
        
    def addSubSection(self, subsection:'Subsection'):
        self.elements.append(subsection)