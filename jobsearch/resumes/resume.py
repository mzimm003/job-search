from typing import (
    List,
    Union,
)
import enum
import datetime
import pickle
from pathlib import Path
from copy import deepcopy

from jobsearch.backend.userprofile import (
    UserProfile,
    WorkExperience,
    Projects,
    Education,
    Skills
    )

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
            websiteLink:str=None,
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
        self.websiteLink:str = '' if websiteLink is None else websiteLink
        self.linkedInLink:str = '' if linkedInLink is None else linkedInLink
        self.gitHubLink:str = '' if gitHubLink is None else gitHubLink
        self.sections:List[Section] = [] if sections is None else sections
        self.ai_tips:dict = {}

    @staticmethod
    def findResumeLinks():
        return list(Path('./Resumes').rglob('*.pkl'))

    @classmethod
    def loadResume(cls, path='./Resumes/main/resume.pkl') -> "Resume":
        r = None
        with open(path,'rb') as f:
            r = pickle.load(f)
        return r

    def setWorkExperienceFromUserProfile(self, work_experience:WorkExperience):
        if not work_experience.is_empty():
            orgs:list[Subsection] = []
            prev_org = None
            prev_end_date = None
            for job in work_experience.jobs:
                if job.organization == prev_org:
                    orgs[-1].addSubSection(Subsection(
                        subject=job.position,
                        startDate=job.start_date,
                        endDate=job.end_date,
                        location=job.location,
                        elements=job.contributions.copy(),
                        type=Subsection.Types.POSITION
                    ))
                else:
                    if orgs:
                        orgs[-1].endDate = prev_end_date
                    orgs.append(Subsection(
                        subject=job.organization,
                        startDate=job.start_date,
                        location=job.location,
                        elements=[Subsection(
                            subject=job.position,
                            startDate=job.start_date,
                            endDate=job.end_date,
                            location=job.location,
                            elements=job.contributions.copy(),
                            type=Subsection.Types.POSITION
                        )],
                        type=Subsection.Types.ORGANIZATION
                        ))
                prev_org = job.organization
                prev_end_date = job.end_date
            orgs[-1].endDate = prev_end_date
            self.addSection(
                Section(
                    title="Work Experience",
                    content=orgs,
                )
            )

    def setProjectsFromUserProfile(self, projects:Projects):
        if not projects.is_empty():
            orgs:list[Subsection] = []
            prev_org = None
            prev_end_date = None
            for project in projects.projects:
                if project.organization == prev_org:
                    orgs[-1].addSubSection(Subsection(
                        subject=project.name,
                        startDate=project.start_date,
                        endDate=project.end_date,
                        elements=project.contributions.copy(),
                        type=Subsection.Types.POSITION
                    ))
                else:
                    if orgs:
                        orgs[-1].endDate = prev_end_date
                    orgs.append(Subsection(
                        subject=project.organization,
                        startDate=project.start_date,
                        elements=[Subsection(
                            subject=project.name,
                            startDate=project.start_date,
                            endDate=project.end_date,
                            elements=project.contributions.copy(),
                            type=Subsection.Types.PROJECT
                        )],
                        type=Subsection.Types.ORGANIZATION
                        ))
                prev_org = project.organization
                prev_end_date = project.end_date
            orgs[-1].endDate = prev_end_date
            self.addSection(
                Section(
                    title="Projects",
                    content=orgs,
                )
            )

    def setEducationFromUserProfile(self, education:Education):
        if not education.is_empty():
            orgs:list[Subsection] = []
            for credential in education.credentials:
                orgs.append(Subsection(
                        subject=credential.institution,
                        location=credential.location,
                        startDate=credential.start_date,
                        endDate=credential.end_date,
                        elements=credential.contributions.copy(),
                        type=Subsection.Types.SCHOOL
                    ))
            self.addSection(
                Section(
                    title="Education",
                    content=orgs,
                )
            )

    def setSkillsFromUserProfile(self, skills:Skills):
        if not skills.is_empty():
            orgs:list[Subsection] = []
            for category, skls in skills.skills.items():
                orgs.append(Subsection(
                        subject=category,
                        elements=skls.copy(),
                        type=Subsection.Types.SKILL
                    ))
            self.addSection(
                Section(
                    title="Skills",
                    content=orgs,
                )
            )

    @classmethod
    def fromUserProfile(cls, organization, job, user_profile:UserProfile) -> "Resume":
        r = cls(
            org = organization,
            job = job,
            name = user_profile.basic_info.name,
            email = user_profile.basic_info.email,
            phone = user_profile.basic_info.phone,
            location = user_profile.basic_info.location,
            websiteLink = user_profile.basic_info.website,
            linkedInLink = user_profile.basic_info.linkedInLink,
            gitHubLink = user_profile.basic_info.gitHubLink,
        )
        r.setWorkExperienceFromUserProfile(user_profile.work_experience)
        r.setProjectsFromUserProfile(user_profile.projects)
        r.setEducationFromUserProfile(user_profile.education)
        r.setSkillsFromUserProfile(user_profile.skills)
        return r

    def saveResume(self):
        job_num = self.job[self.job.rfind('-')+1:]
        if not Path('./Resumes/{}'.format(self.org)).exists():
            Path('./Resumes/{}'.format(self.org)).mkdir(parents=True, exist_ok=True)
        with open('./Resumes/{}/{}.pkl'.format(self.org, job_num),'wb') as f:
            pickle.dump(self, f)

    def setAITips(self, tips):
        self.ai_tips = tips
    
    def getAITips(self):
        return self.ai_tips

    def setOrg(self, org):
        self.org = org

    def getOrg(self):
        return self.org

    def setJob(self, job):
        self.job = job

    def getJob(self):
        return self.job

    def getTopSkills(self, num=20):
        ret = []
        ordered_list = []
        if self.ai_tips:
            penalties = {}
            for skl in sorted(self.ai_tips["Skills"].items(), key=lambda x: x[1]['rating'], reverse=True):
                temp = deepcopy(skl)
                temp[1]['keywords'] = ','.join(skl[1]['keywords'])
                if not temp[1]['keywords'] in penalties:
                    penalties[temp[1]['keywords']] = 0
                temp[1]['rating'] -= (10 * penalties[temp[1]['keywords']])
                ordered_list.append(temp)
                penalties[temp[1]['keywords']] += 1
            ordered_list = sorted(ordered_list, key=lambda x: x[1]['rating'], reverse=True)

        return list(ordered_list)[:num]

    def addSection(self, section:'Section'):
        self.sections.append(section)

    def getSections(self)->List['Section']:
        return self.sections

    def asString(self, bulletsOnly=False, skillsOnly=False, skipEdu=False, skipSkl=False, skillSep=', ', lineNums=False, asDict=False):
        s = self.__stringList(bulletsOnly=bulletsOnly, skillsOnly=skillsOnly, skillSep=skillSep, skipEdu=skipEdu, skipSkl=skipSkl)

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

    def __stringList(self, bulletsOnly=False, skillsOnly=False, skillSep=', ', skipEdu=False, skipSkl=False):
        s = []
        if not bulletsOnly and not skillsOnly:
            s.append(self.name)
        for sec in self.sections:
            if not ((skipEdu and sec.title=="Education") or
                    (skipSkl and sec.title=="Skills")):
                if not bulletsOnly and not skillsOnly:
                    s.append(sec.title+":")
                for con in sec.content:
                    if not bulletsOnly and not skillsOnly:
                        s.append('\t'+con.subject)
                    csv = []
                    for elm in con.elements:
                        if isinstance(elm, str):
                            if con.type == Subsection.Types.SKILL:
                                csv.append(elm)
                            else:
                                if not skillsOnly:
                                    s.append('\t\t-'+elm)
                        else:
                            if elm.type == Subsection.Types.PROJECT or elm.type == Subsection.Types.POSITION:
                                if not bulletsOnly and not skillsOnly:
                                    s.append('\t\t'+elm.subject)
                                for e in elm.elements:
                                    if not skillsOnly:
                                        s.append('\t\t\t-'+e)
                            elif elm.type == Subsection.Types.SKILL:
                                if not bulletsOnly:
                                    if skillSep == '\n':
                                        s.append(elm.subject)
                                        for e in elm.elements:
                                            s.append(e)
                                    else:
                                        s.append('\t\t'+elm.subject+skillSep+skillSep.join([e for e in elm.elements]))
                    if csv:
                        if not bulletsOnly:
                            if skillSep == '\n':
                                for e in csv:
                                    s.append(e)
                            else:
                                s.append('\t\t'+skillSep.join(csv))
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

    def removeSubSection(self, subsection:'Subsection'):
        self.content.remove(subsection)

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
    
    def setElements(self, elements):
        #Written as a slower process to preserve attribute address
        i = 0
        for e in elements:
            if i < len(self.elements):
                self.elements[i] = e
            else:
                self.elements.append(e)
            i += 1
        if i < len(self.elements):
            del_idx = i
            org_len = len(self.elements)
            while i < org_len:
                del self.elements[del_idx]
                i += 1

    def addSubSection(self, subsection:'Subsection'):
        self.elements.append(subsection)

    def removeSubSection(self, subsection:'Subsection'):
        self.elements.remove(subsection)