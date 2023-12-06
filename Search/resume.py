from typing import (
    List,
    Union,
)
import enum
import datetime
class Resume:
    def __init__(
            self,
            name:str = None,
            email:str = None,
            phone:str = None,
            location:str = None,
            linkedInLink:str = None,
            gitHubLink:str = None,
            sections:List['Section'] = None,
            ):
        self.name:str = '' if name is None else name
        self.email:str = '' if email is None else email
        self.phone:str = '' if phone is None else phone
        self.location:str = '' if location is None else location
        self.linkedInLink:str = '' if linkedInLink is None else linkedInLink
        self.gitHubLink:str = '' if gitHubLink is None else gitHubLink
        self.sections:List[Section] = [] if sections is None else sections

class Section:
    def __init__(
            self,
            title = None,
            content = None,
            ) -> None:
        self.title:str = '' if title is None else title
        self.content:List[Subsection] if content is None else content

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
            ) -> None:
        self.subject:str = '' if subject is None else subject
        self.startDate:datetime.date = datetime.date.today() if startDate is None else startDate
        self.endDate:datetime.date = datetime.date.today() if endDate is None else endDate
        self.location:str = '' if location is None else location
        self.elements:Union(List[Subsection],List[str]) = [] if elements is None else elements


