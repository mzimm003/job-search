import dataclasses
import datetime
from pathlib import Path
import json
import typing

@dataclasses.dataclass
class NestingDataClass:
    @classmethod
    def from_dict(cls, dct:dict):
        ret = {}
        for field in dataclasses.fields(cls):
            ret[field.name] = NestingDataClass.instantiate(
                field.type,
                dct[field.name]
                )
        return cls(**ret)
    
    @staticmethod
    def instantiate(cls, inp):
        inst = None
        if isinstance(cls, type):
            if issubclass(cls, NestingDataClass):
                inst = cls.from_dict(inp)
            elif dataclasses.is_dataclass(cls):
                inst = cls(**inp)
            else:
                inst = cls(inp)
        elif isinstance(cls, typing.GenericAlias):
            if cls.__origin__ is dict:
                inst = cls.__origin__(
                    (k, NestingDataClass.instantiate(cls.__args__[-1], v))
                    for k,v
                    in inp.items())
            else:
                inst = cls.__origin__(
                    NestingDataClass.instantiate(cls.__args__[-1], x)
                    for x
                    in inp)
        return inst
    
    def is_empty(self):
        return self == self.__class__()

    def set(self, attribute:str, dct:dict):
        obj = getattr(self, attribute)
        for field in dataclasses.fields(obj):
            if dataclasses.is_dataclass(field.type):
                sub_obj = getattr(obj, field.name)
                dct[field.name] = self._set_helper(sub_obj, dct[field.name])
                    
            elif isinstance(field.type, typing.GenericAlias):
                if field.type.__origin__ is dict:
                    dct[field.name] = field.type.__origin__(
                        (k, self._set_helper(getattr(obj, field.name)[k], v))
                        for k,v
                        in dct[field.name].items())
                else:
                    dct[field.name] = field.type.__origin__(
                        self._set_helper(getattr(obj, field.name)[i], x)
                        for i,x
                        in enumerate(dct[field.name]))
        setattr(self, attribute, dataclasses.replace(obj, **dct))

    def _set_helper(self, obj, dct):
        ret = None
        if isinstance(obj, NestingDataClass):
            obj.set(dct)
            ret = obj
        else:
            ret = dataclasses.replace(
                obj,
                **dct)
        return ret

@dataclasses.dataclass
class BasicInfo:
    name:str = ""
    email:str = ""
    phone:str = ""
    location:str = ""
    linkedIn_link:str = ""
    github_link:str = ""
    website:str = ""
    summary:str = ""

@dataclasses.dataclass
class Job:
    organization:str = ""
    position:str = ""
    location:str = ""
    start_date:datetime.date = datetime.date.today()
    end_date:datetime.date = datetime.date.today()
    contributions:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class WorkExperience(NestingDataClass):
    jobs:list[Job] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Project:
    organization:str = ""
    name:str = ""
    start_date:datetime.date = datetime.date.today()
    end_date:datetime.date = datetime.date.today()
    contributions:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Projects(NestingDataClass):
    projects:list[Project] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Credential:
    institution:str = ""
    location:str = ""
    start_date:datetime.date = datetime.date.today()
    end_date:datetime.date = datetime.date.today()
    contributions:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Education(NestingDataClass):
    credentials:list[Credential] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Skills(NestingDataClass):
    skills:dict[str,list[str]] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class UserProfile(NestingDataClass):
    FILENAME = "userprofile.json"
    basic_info:BasicInfo = dataclasses.field(default_factory=BasicInfo)
    work_experience:WorkExperience = dataclasses.field(default_factory=WorkExperience)
    projects:Projects = dataclasses.field(default_factory=Projects)
    education:Education = dataclasses.field(default_factory=Education)
    skills:Skills = dataclasses.field(default_factory=Skills)

    @classmethod
    def by_directory(cls, directory):
        directory = Path(directory)
        profile_file = directory / cls.FILENAME
        profile = None
        if profile_file.exists():
            profile = cls.from_json(profile_file)
        else:
            profile = cls()
        return profile

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