import google.generativeai as genai
from statistics import mean
from collections import Counter
from jobsearch.resumes.resume import Resume
import time
import abc

class Model(abc.ABC):
    def __init__(self, api_key) -> None:
        self.model = self.load(api_key=api_key)

    @abc.abstractmethod
    def generate_content(self, prompt):
        ...

    @abc.abstractmethod
    def load(self, api_key):
        ...

class GoogleGemini(Model):
    model:genai.GenerativeModel
    def __init__(self, api_key) -> None:
        super().__init__(api_key=api_key)

    def load(self, api_key):
        genai.configure(api_key=api_key)
        config = genai.GenerationConfig(
            # candidate_count = 4,
            # stop_sequences = None,
            # max_output_tokens = None,
            temperature = .5,
            top_p = .8,
            top_k = 1024
            )
        return genai.GenerativeModel('gemini-pro', generation_config=config)

    def generate_content(self, prompt):
        return self.model.generate_content(prompt)

class LLM:
    def __init__(self, api_key, num_requests = 6) -> None:
        self.num_requests = num_requests
        self.model = Model(api_key=api_key)

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
