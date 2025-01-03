import dataclasses
import datetime
from pathlib import Path
import json
import typing

def json_serializer(obj):
    if isinstance(obj, (datetime.date)):
        return {"__datetime.date__":obj.isoformat()}
    raise TypeError ("Type %s not serializable" % type(obj))

def json_deserializer(obj):
    if "__datetime.date__" in obj:
        return datetime.date.fromisoformat(obj["__datetime.date__"])
    return obj

@dataclasses.dataclass
class DataClass:
    def as_dict(self):
        return dataclasses.asdict(self)

    def fields(self):
        return dataclasses.fields(self)

    def get(self, item:str):
        return getattr(self, item)

    def set(self, dct:dict):
        for field in dataclasses.fields(self):
            if field.name in dct:
                sub_obj = getattr(self, field.name)
                if dataclasses.is_dataclass(field.type):
                    dct[field.name] = self._set_helper(sub_obj, dct[field.name])
                        
                elif isinstance(field.type, typing.GenericAlias):
                    content_class = field.type.__args__[-1]
                    if field.type.__origin__ is dict:
                        dct[field.name] = field.type.__origin__(
                            (
                                k,
                                self._set_helper(
                                    sub_obj[k] if k in sub_obj else content_class(),
                                    v))
                            for k,v
                            in dct[field.name].items())
                    else:
                        dct[field.name] = field.type.__origin__(
                            self._set_helper(
                                sub_obj[i] if i < len(sub_obj) else content_class(),
                                x)
                            for i,x
                            in enumerate(dct[field.name]))
        updated_instance = dataclasses.replace(self, **dct)
        for field in dataclasses.fields(self):
            setattr(
                self,
                field.name,
                getattr(updated_instance, field.name))

    def _set_helper(self, obj, data):
        ret = obj
        if isinstance(obj, NestingDataClass):
            obj.set(data)
            ret = obj
        elif dataclasses.is_dataclass(obj):
            ret = dataclasses.replace(
                obj,
                **data)
        else:
            if not data == {}:
                if type(obj) != type(data):
                    raise ValueError("Object {} cannot be replaced by data {}".format(obj, data))
                ret = data
        return ret

    def add_new_list_item(self, list_name:str):
        l = getattr(self, list_name)
        self.set({list_name:[{} for i in range(len(l)+1)]})

    def remove_list_item(self, list_name:str, idx:int):
        l = getattr(self, list_name)
        del l[idx]

@dataclasses.dataclass
class NestingDataClass(DataClass):
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
    
    def copy(self):
        return self.from_dict(
            dataclasses.asdict(self)
        )
    
    def is_empty(self):
        return self == self.__class__()

@dataclasses.dataclass
class BasicInfo(DataClass):
    name:str = ""
    email:str = ""
    phone:str = ""
    location:str = ""
    linkedIn_link:str = ""
    github_link:str = ""
    website:str = ""
    summary:str = ""

@dataclasses.dataclass
class Job(DataClass):
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
class Project(DataClass):
    organization:str = ""
    name:str = ""
    start_date:datetime.date = datetime.date.today()
    end_date:datetime.date = datetime.date.today()
    contributions:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Projects(NestingDataClass):
    projects:list[Project] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Credential(DataClass):
    institution:str = ""
    location:str = ""
    start_date:datetime.date = datetime.date.today()
    end_date:datetime.date = datetime.date.today()
    contributions:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Education(NestingDataClass):
    credentials:list[Credential] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class SkillSet(DataClass):
    topic:str = ""
    skills:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Skills(NestingDataClass):
    skill_sets:list[SkillSet] = dataclasses.field(default_factory=list)

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
                configs = json.load(f, object_hook=json_deserializer)
                ret = cls.from_dict(configs)
        else:
            ret = cls(**dict())
        return ret

    def to_json(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(dataclasses.asdict(self), f, default=json_serializer)