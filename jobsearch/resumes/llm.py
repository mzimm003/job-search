import google.generativeai as genai
from statistics import mean
from collections import Counter
from jobsearch.resumes.resume import Resume
import time
import abc
import enum
import json
import dataclasses
from pathlib import Path

@dataclasses.dataclass
class ModelOptions:
    model_name:str

class Model(abc.ABC):
    options:ModelOptions
    def __init__(self, options:dict=None) -> None:
        options = {} if options is None else options
        self.options = self.options(**options)

    @abc.abstractmethod
    def generate_content(self, prompt):
        ...

    @abc.abstractmethod
    def set_api(self, api_key):
        ...

    @classmethod
    def default_options(cls):
        return cls.options()
    
    def get_options(self):
        return self.options
    
    @classmethod
    def default_options_asdict(cls):
        return dataclasses.asdict(cls.options())
    
    def get_options_asdict(self):
        return dataclasses.asdict(self.options)
    
    def set_options(self, options:dict|ModelOptions):
        if isinstance(options, ModelOptions):
            options = dataclasses.asdict(options)
        self.options = dataclasses.replace(self.options, **options)


class GoogleGemini(Model):
    @dataclasses.dataclass
    class Options(ModelOptions):
        model_name:str = "gemini-pro"
        temperature:float = 0.5
        top_p:float = 0.8
        top_k:int = 1024
    
    model:genai.GenerativeModel
    options:Options = Options

    def __init__(self, options: dict = None) -> None:
        super().__init__(options)
        options = self.get_options_asdict()
        model_name = options.pop("model_name")
        self.model = genai.GenerativeModel(model_name)

        self.gen_config = genai.GenerationConfig(
            **options
            )

    def set_api(self, api_key):
        genai.configure(api_key=api_key)

    def generate_content(self, prompt):
        return self.model.generate_content(
            prompt,
            generation_config=self.get_options())

class LLMAPIOptions(enum.Enum):
    Google = GoogleGemini
    OpenAI = ... #TODO
    Anthropic = ... #TODO
    Microsoft = ... #TODO

    def __call__(self, options):
        return self.value(options=options)

@dataclasses.dataclass
class ModelCatalogEntry:
    api_option:LLMAPIOptions
    model_options:ModelOptions

@dataclasses.dataclass
class LLMCatalog:
    models:dict[str, ModelCatalogEntry]
    default:str = ""
    
    def __contains__(self, item):
        return item in self.models

    @classmethod
    def from_json(cls, json_path):
        ret = None
        json_path = Path(json_path)
        if json_path.exists():
            with open(json_path, 'r') as f:
                configs = json.load(f)
                models = {}
                for m,v in configs["models"].items():
                    model = LLMAPIOptions[v["api_option"]].value
                    v["model_options"] = model.options(**v["model_options"])
                    models[m] = ModelCatalogEntry(**v)
                configs["models"] = models
                ret = cls(**configs)
        else:
            ret = cls(**dict(models={}))
        return ret

    def to_json(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(dataclasses.asdict(self), f)

    def set_default(self, name:str):
        self.default = name

    def load_model(self, name:str)->Model:
        model = None
        if name in self.models:
            model_class = LLMAPIOptions[self.models[name].api_option].value
            model = model_class(dataclasses.asdict(self.models[name].model_options))
            self.set_default(name)
        return model
    
    def add_model(self, name:str, model:LLMAPIOptions):
        self.models[name] = ModelCatalogEntry(
            api_option = model.name,
            model_options = model.value.default_options())
        
    def delete_model(self, name:str):
        del self.models[name]
        if name == self.default:
            self.default = list(self.models.keys())[0]
    
    def set_model_options(self, name:str, options:dict|ModelOptions):
        if isinstance(options, ModelOptions):
            options = dataclasses.asdict(options)
        entry = self.models[name]
        entry.model_options = dataclasses.replace(entry.model_options, **options)

    def get_llm_options(self):
        return list(self.models.keys())

class LLM:
    def __init__(self, config_json_path, num_requests = 6) -> None:
        self.num_requests = num_requests
        self.config_json_path = config_json_path
        self.catalog = LLMCatalog.from_json(config_json_path)
        self.model = self.catalog.load_model(self.catalog.default)

    def save_catalog(self):
        self.catalog.to_json(self.config_json_path)
    
    def get_catalog_options(self):
        return self.catalog.get_llm_options()
    
    def get_catalog_default_option(self):
        return self.catalog.default

    def set_model(self, name:str, api_option:LLMAPIOptions=None):
        if not name in self.catalog:
            self.catalog.add_model(name, model=api_option)
        self.model = self.catalog.load_model(name=name)

    def delete_model(self, name:str):
        self.catalog.delete_model(name=name)
        self.set_model(self.catalog.default)
    
    def set_api(self, api_key):
        if api_key:
            self.model.set_api(api_key=api_key)
    
    def get_model_API_by_name(self, name:str):
        return self.catalog.models[name].api_option
    
    def get_model_API(self):
        return LLMAPIOptions(self.model.__class__)

    def set_model_options(self, options):
        self.catalog.set_model_options(self.catalog.default, options=options)
        self.model.set_options(options=options)

    def set_model_options_by_name(self, name, options):
        self.catalog.set_model_options(name, options=options)
        if name == self.catalog.default:
            self.model = self.catalog.load_model(name)

    def get_model_options(self):
        return self.model.get_options()
    
    def get_model_options_by_name(self, name:str):
        return dataclasses.asdict(self.catalog.models[name].model_options)

    def getTips(self, resume:Resume, jobDesc):
        prompt = """** Prompt **\n\nProvide the key terms for the following job description, returning a simple bulleted list, and no header.\n\n** Example **\n\n- key term 1\n- key term 2\n...\n\n** Job Description **\n\n{}""".format(jobDesc)
        resp = self.model.generate_content(prompt)
        key_terms = resp.text

        
        # Gemini model does not adequately update resume in meaningful way. Instead rating system will be used
        # to inform user of usefulness of resume experience item as well as keywords which they might be able
        # to manually incorporate. Rating will be performed multiple times to reduce impact of random outlier
        # responses from model. 
        resume_experience = resume.asString(bulletsOnly=True, skipEdu=True, lineNums=True)
        prompt = """**Resume:**\n\n{}\n\n**Key Terms:**\n\n{}\n\n**Prompt**\n\nFor each line of the Resume, provide a rating on a scale from 1 to 10 on how related it is to the Key Terms. Results should be presented in a table of the format | Line | Rating | Top 3 Related Key Terms |""".format(resume_experience, key_terms)
        table_results = {"Experience":{},"Skills":{},"Key Terms":key_terms}
        for i in range(self.num_requests):
            resp = self.model.generate_content(prompt)
            tab = self.interpretTable(resp.text)
            table_results["Experience"] = self.combineTableInterpretations(table_results["Experience"], tab)
        table_results["Experience"] = self.finalizeTableResults(table_results["Experience"])

        resume_skills = resume.asString(skillsOnly=True, skillSep='\n', lineNums=True)
        prompt = """**Resume Skills:**\n\n{}\n\n**Key Terms:**\n\n{}\n\n**Prompt**\n\nFor each line of the Resume Skills, provide a rating on a scale from 1 to 10 on how related it is to the Key Terms. Results should be presented in a table of the format | Line | Rating | Top 3 Related Key Terms |""".format(resume_skills, key_terms)
        for i in range(self.num_requests):
            resp = self.model.generate_content(prompt)
            tab = self.interpretTable(resp.text)
            table_results["Skills"] = self.combineTableInterpretations(table_results["Skills"], tab)
        table_results["Skills"] = self.finalizeTableResults(table_results["Skills"])

        return table_results
    
    def interpretTable(self, table):
        t = {}
        for i, line in enumerate(table.split('\n')):
            if i != 0:
                elms = line.split(' | ')
                if len(elms) == 3:
                    t[int(elms[0].removeprefix('| '))] = {'rating':[float(elms[1])], 'keywords':elms[2].removesuffix(' |').split(', ')}
        return t

    def combineTableInterpretations(self, table1, table2):
        ct = {}
        unvisited_t2 = {k:True for k in table2.keys()}
        for l, t1 in table1.items():
            if l in table2:
                ct[l] = {'rating':t1['rating']+table2[l]['rating'], 'keywords':t1['keywords']+table2[l]['keywords']}
                unvisited_t2[l] = False
            else:
                ct[l] = {'rating':t1['rating'], 'keywords':t1['keywords']}
        for l, uv in unvisited_t2.items():
            if uv:
                ct[l] = {'rating':table2[l]['rating'], 'keywords':table2[l]['keywords']}
        return ct

    def finalizeTableResults(self, table):
        res = {}
        for l, r in table.items():
            keyWordCounts = Counter(r['keywords'])
            top3KeyWords = list(sorted(keyWordCounts.keys(), key=lambda x:keyWordCounts[x], reverse=True))[:3]
            res[l] = {'rating':mean(r['rating']), 'keywords':top3KeyWords}
        return res
