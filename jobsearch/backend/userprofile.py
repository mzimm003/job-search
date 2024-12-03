import dataclasses
import datetime
from pathlib import Path
import json

@dataclasses.dataclass
class BasicInfo:
    name:str =  ''
    email:str =  ''
    phone:str =  ''
    location:str =  ''
    linkedInLink:str =  ''
    gitHubLink:str =  ''
    website:str =  ''

@dataclasses.dataclass
class Job:
    organization:str
    position:str
    location:str
    start_date:datetime.date
    end_date:datetime.date
    contributions:list[str]

@dataclasses.dataclass
class WorkExperience:
    jobs:list[Job]

@dataclasses.dataclass
class Project:
    organization:str
    name:str
    start_date:datetime.date
    end_date:datetime.date
    contributions:list[str]

@dataclasses.dataclass
class Projects:
    projects:list[Project]

@dataclasses.dataclass
class Credential:
    institution:str
    location:str
    start_date:datetime.date
    end_date:datetime.date
    contributions:list[str]

@dataclasses.dataclass
class Education:
    credentials:list[Credential]

@dataclasses.dataclass
class Skills:
    skills:dict[str,list[str]]

@dataclasses.dataclass
class UserProfile:
    summary:str = ""
    basic_info:BasicInfo = BasicInfo()
    work_experience:WorkExperience = WorkExperience()
    projects:Projects = Projects()
    education:Education = Education()
    skills:Skills = Skills()

    @classmethod
    def from_dict(cls, dct:dict):
        ret = {}
        for field in dataclasses.fields(cls):
            inst = None
            if field.type in [str]:
                inst = field.type(dct[field.name])
            else:
                inst = field.type.from_dict(dct[field.name])
            ret[field.name] = inst
        return cls(**ret)

    @classmethod
    def from_json(cls, json_path):
        ret = None
        json_path = Path(json_path)
        if json_path.exists():
            with open(json_path, 'r') as f:
                configs = json.load(f)
                ret = cls.from_dict(configs)
        else:
            ret = cls(**dict())
        return ret

    def to_json(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(dataclasses.asdict(self), f)