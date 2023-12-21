import google.generativeai as genai
from statistics import mean
from collections import Counter

class LLM:
    def __init__(self, api_key, num_requests = 6) -> None:
        genai.configure(api_key=api_key)
        config = genai.GenerationConfig(
            # candidate_count = 4,
            # stop_sequences = None,
            # max_output_tokens = None,
            temperature = .5,
            top_p = .8,
            top_k = 1024
            )
        self.num_requests = num_requests
        self.model = genai.GenerativeModel('gemini-pro', generation_config=config)

    def getTips(self, resume, jobDesc):
        # prompt = '''Please review the following resume and job description, both labeled and contained in brackets below. For the 'Projects' and 'Work Experience' sections, please rewrite each bullet (denoted by a "-") from the resume, as if you were me, with the intent to incorporate the most important terms and concepts from the job description, or otherwise suggest removing the bullet if it is irrelevant. These rewrites should be provided as part of a table, which will also include the bullet as it existed originally, and the reason for the rewrite (either the term or concept identified in the job description, or irrelevancy). Then, after the table, for the 'Skills' section, select and list the top 10-20 comma separated values of the section relevant to the job.'''
        # prompt = "{}\n\nResume:{{{}}}\n\nJob Description:{{{}}}".format(prompt, resume, jobDesc)
        # prompt = '''Please review the following resume and job description, both labeled and contained in brackets below. Consider how you would incorporate the most important terms and concepts from the job description into the lines preceeded by "-". Present your rewrites as a table with 3 columns. In the first column, provide the original content from the resume. In the second column, provide your revision. In the last column, provide the reason the revision makes the description more relevant to the important terms and concepts from the job description.'''
        # prompt = "{}\n\nResume:{{{}}}\n\nJob Description:{{{}}}".format(prompt, resume, 
        # jobDesc)
        # prompt = """**Prompt:**\n\nGiven a resume and a job description, generate a table of revisions to the resume that focus on important terms and concepts from the job description. The table should include the line number of the original resume text, the revised resume text, and a justification for the revision.\n\n**Instructions:**\n\n1. Use the following template to generate a table of revisions:\n\n| Resume Line Number | Revised Resume Text | Justification |\n|---|---|---|\n\n2. For each row in the table, include the following information:\n\n* The line number from the original resume text\n* The revised resume text\n* A justification for the revision\n\n3. Make sure that the revisions are specific and relevant to the job description.\n\n4. Use the [Job Description Analyzer](https://job-description-analyzer.com/) to help you identify important terms and concepts in the job description.\n\n**Example:**\n\n| Resume Line Number | Revised Resume Text | Justification |\n|---|---|---|\n|0|A revision of line 0 incorporating a keyword from the job description|Due to importance of keyword|Job emphasizes keyword which this resume experience highlights.|\n|1|A revision of line 1 adjusted to highlight its relevance to an important concept in the job description|Job emphasizes important concept|\n\n**Given Resume:**\n\n{}\n\n**Given Job Description:**\n\n{}""".format(resume, jobDesc)
        # prompt = """**Prompt:**\n\nYou are a resume writer who has been hired by a job seeker to help them revise their resume for a specific job posting. The job posting is provided below along with the job seeker's resume so far.\n\n**Instructions:**\n\n1. Read the job posting carefully and identify the key skills and qualifications that the employer is looking for.\n2. Review the job seeker's resume and identify any areas that could be improved.\n3. Make suggestions for how the job seeker can highlight their skills and qualifications in a way that is relevant to the job posting.\n4. Provide the job seeker with a revised resume that is tailored to the specific job posting, revising only specific lines of the job seeker's resume.\n\n**Job Seeker's Resume:**\n\n{}\n\n**Job Posting:**\n\n{}""".format(resume, jobDesc)
        # prompt = """\n**Prompt:**\n\n**Job Description:** {}\n\n**My Resume:** {}\n\n**Specific Instructions:**\n\n* **Identify and highlight** important terms and concepts from the job description.\n* **Provide a table of revisions** that includes the following columns:\n    * Original line number from my resume\n    * Proposed revision\n    * Justification for the revision based on relevance to job description\n* **Tone:** Professional, confident, and persuasive.\n\n**Additional Notes:**\n\n* Please feel free to be creative and use your best judgment when making revisions.\n* I am open to any suggestions that you may have to improve my resume.\n\n**Thank you for your help!**\n""".format(jobDesc, resume)
        # prompt = """\n**Prompt:**\n\n**Job Description:** {}\n\n**My Resume:** {}\n\n**Specific Instructions:**\n\n* For the 'Projects' and 'Work Experience' sections, please rewrite each bullet (denoted by a "-") from the resume, as if you were me, with the intent to incorporate the most important terms and concepts from the job description, or otherwise suggest removing the bullet if it is irrelevant to the job description. These rewrites should be provided as part of a table, which will also include the bullet as it existed originally, and the reason for the rewrite (either the term or concept identified in the job description, or irrelevancy). Then, after the table, for the 'Skills' section, select and list the top 10-20 comma separated values of the section relevant to the job.\n\n **Tone:** Professional, confident, and persuasive.\n\n**Additional Notes:**\n\n* Please feel free to be creative and use your best judgment when making revisions.\n* I am open to any suggestions that you may have to improve my resume.\n\n**Thank you for your help!**\n""".format(jobDesc, resume)
        # prompt = """\n**Prompt:**\n\n**Job Description:** {}\n\n**My Resume:** {}\n\n**Specific Instructions:**\n\n *Rewrite* each from the my resume, as if you were me. Consider whether the line describes experience relevant to the job description. If the experience is relevant, the rewrite should incorporate the most important terms and concepts from the job description. If the experience is not relevant, suggest removing the bullet. Provide these rewrites as a table where each row describes the original resume line number, the suggested rewrite, and the a succinct reasoning for the suggestion.""".format(jobDesc, resume)
        # prompt = """\n**Prompt:**\n\n**Job Description:**\n{}\n\n**My Resume:**\n{}\n\n**Specific Instructions:**\n\n*Consider* how to modify the experience described in each line from my resume that would help the content incorporate either specific keywords or general concepts from the job description, without changing its meaning.\n*Provide a table* with the following columns:\n\t*the line number from the original resume.*\n\t*A label, either 'revelevant' if the original resume experience can be applied to the job description in any capacity, or 'irrelevant' if the meaning of the original resume experience would have to be completely altered to be applicable to the job description.*\n\t*The suggested rewrite.*\n\t*reasoning for the suggestion in a few words.*""".format(jobDesc, resume)
        # prompt = """\n**Prompt:**\n\n**Job Description:** {}\n\n**My Resume:** {}\n\n**Specific Instructions:**\n\n \n\nFor each line of experience in my resume, answer the following prompt:\n*Can I reword this to incorporate important language from the job description, and if so, how?*""".format(jobDesc, resume)
        #  Then, after the table, for the 'Skills' section, select and list the top 10-20 comma separated values of the section relevant to the job.\n\n **Tone:** Professional, confident, and persuasive.\n\n**Additional Notes:**\n\n* Please feel free to be creative and use your best judgment when making revisions.\n* I am open to any suggestions that you may have to improve my resume.\n\n**Thank you for your help!**\n


        prompt = """Provide the key terms for the following job description:\n\n{}""".format(jobDesc)
        resp = self.model.generate_content(prompt)
        key_terms = resp.text

        
        # Gemini model does not adequately update resume in meaningful way. Instead rating system will be used
        # to inform user of usefulness of resume experience item as well as keywords which they might be able
        # to manually incorporate. Rating will be performed multiple times to reduce impact of random outlier
        # responses from model. 
        prompt = """**Resume:**\n\n{}\n\n**Key Terms:**\n\n{}\n\n**Prompt**\n\nFor each line of the Resume, provide a rating on a scale from 1 to 10 on how related it is to the Key Terms. Results should be presented in a table of the format | Line | Rating | Top 3 Related Keywords |""".format(resume, key_terms)
        table_results = {}
        for i in range(self.num_requests):
            resp = self.model.generate_content(prompt)
            tab = self.interpretTable(resp.text)
            self.combineTableInterpretations(table_results, tab)
        table_results = self.finalizeTableResults(table_results)
        return table_results
    
    def interpretTable(self, table):
        t = {}
        for line in table.split('\n'):
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
        r = {}
        for l, r in table.items():
            keyWordCounts = Counter(r['keywords'])
            top3KeyWords = list(sorted(keyWordCounts.keys(), key=lambda x:keyWordCounts[x], reverse=True))[:3]
            r[l] = {'rating':mean(table['rating']), 'keywords':top3KeyWords}
        return r
