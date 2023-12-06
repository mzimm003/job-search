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

    def addSection(self, section:'Section'):
        self.sections.append(section)

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
        self.startDate:datetime.date = datetime.date.today() if startDate is None else startDate
        self.endDate:datetime.date = datetime.date.today() if endDate is None else endDate
        self.location:str = '' if location is None else location
        self.elements:List[Subsection]|List[str] = [] if elements is None else elements
        self.type:Subsection.Types = Subsection.Types.ORGANIZATION if type is None else type
        
    def addSubSection(self, subsection:'Subsection'):
        self.elements.append(subsection)

def main():
    import pickle
    import datetime
    r = None
    with open('resume.pkl','rb') as f:
        r:Resume = pickle.load(f)
    inp = [
        {
            'subject':'Senior Recoverable Revenue Accountant',
            'startDate':datetime.date(2017, 1, 1),
            'endDate':datetime.date(2021, 7, 1),
            'elements':[
                'Developed tools in excel, leveraging AI and machine learning techniques, to provide for faster, more accurate analysis, review, and calculation processes.',
                'Wrote documentation and hosted training to support the utilization of these 10+ tools.',
                'Led training for all job facets from the technical to the analytical for 50+ persons since 2017, including new team members, entire departments after reorganization, and contracted parties abroad.',
                'Prepared analyses and summaries for upper and executive management to inform multi-million dollar business decisions.',
                'Collaborated with IT to develop and test process improvements, reducing manual workloads by 100+ hours.',
                'Oversaw cycle work done for 40+ properties and 1,000s of abstractions of tenant agreements into JD Edwards E1 performed by junior team members.'
                ],
            'type':Subsection.Types.POSITION
        },
        {
            'subject':'Recoverable Revenue Accountant',
            'startDate':datetime.date(2015, 5, 1),
            'endDate':datetime.date(2016, 12, 1),
            'elements':[
                'Abstracted, and maintained, the appropriate expense recovery terms into JD Edwards E1 from dozens of tenant agreement forms (lease, amendment, easement, etc.) for 1,000s of tenants.',
                'Reconciled, forecasted, and budgeted recoverable revenues for 1000s of tenants.',
                'Supported Accounts Receivable in the resolution of 100s of tenant queries and disputes related to Recoverable Revenues via a JIRA ticketing system. ',
                'Assisted Center Management, Regional Analyst, Regional Finance Directors, and Shared Services with requests and questions relating to Recoverable Revenues.',
                'Identified and implemented process improvements.',
            ],
            'type':Subsection.Types.POSITION
        },
        {
            'subject':'AR Specialist',
            'startDate':datetime.date(2013, 10, 1),
            'endDate':datetime.date(2015, 5, 1),
            'elements':[
                'Maintained 1000s of mall tenants\' ledger\'s accuracy through thorough research and analysis.',
                'Communicated discrepancies in billings and payments received intelligibly and diplomatically.',
                'Collaborated interdepartmentally and with peers to achieve the above for over a thousand tenants at once.',
            ],
            'type':Subsection.Types.POSITION
        },
    ]
    for d in inp:
        r.sections[1].content[0].addSubSection(Subsection(**d))
    
    
    inp = [
        {
            'subject':"GEORGIA INSTITUTE OF TECHNOLOGY",
            'location':"Atlanta, GA",
            'elements':[
                "Master's in Computer Science - Machine Learning",
                "GPA: 4.0/4.0"
            ],
            'type':Subsection.Types.SCHOOL
        },
        {
            'subject':"EL CAMINO COLLEGE",
            'location':"Torrance, CA",
            'elements':[
                "Attended Supplementary Computer Science and Technology classes",
                "Preparation for Master's program - no credential obtained",
                "GPA: 4.0/4.0",
            ],
            'type':Subsection.Types.SCHOOL
        },
        {
            'subject':"UNIVERSITY OF CALIFORNIA, LOS ANGELES EXTENSION",
            'location':"Los Angeles, CA",
            'elements':[
                "Completed Certificate of Accounting",
                "GPA: 3.94/4.0",
            ],
            'type':Subsection.Types.SCHOOL
        },
        {
            'subject':"UNIVERSITY OF CALIFORNIA, RIVERSIDE",
            'location':"Riverside, CA",
            'elements':[
                "Completed Bachelor of Science in Mathematics",
                "GPA: 2.78/4.0",
            ],
            'type':Subsection.Types.SCHOOL
        },
    ]

    for d in inp:
        r.sections[2].addSubSection(Subsection(**d))

    r.sections[3].addSubSection(Subsection("Languages", elements=["Python", "C++", "Java", "C#"], type=Subsection.Types.SKILL))
    r.sections[3].addSubSection(Subsection("Libraries", elements=["NumPy", "PyTorch", "Ray.RLLib", "Sklearn", "MatPlotLib", "Gym", "Pandas", "Pillow", "OpenCV"], type=Subsection.Types.SKILL))
    r.sections[3].addSubSection(Subsection("Technologies", elements=["Visual Studio", "VS Code", "Git", "Anaconda", "Docker", "Unity", "Jupyter Notebooks", "CUDA", "LaTex", "Inkscape", "Linux", "Windows", "Microsoft Office"], type=Subsection.Types.SKILL))
    r.sections[3].addSubSection(Subsection("Studies", elements=[
        Subsection("Artificial Intelligence", elements=["Graph search", "Heuristic search", "Adversarial search", "Bayesian Networks", "Markov Chains", "K-means clustering", "Decision trees", "Ensemble learners", "Bagging", "Boosting", "Gaussian mixture models", "Hidden Markov models"], type=Subsection.Types.SKILL),
        Subsection("Game Artificial Intelligence", elements=["Pathfinding", "Navigation mesh", "Fuzzy logic", "Procedural content generation", "Finite state machines", "Ballistic trajectory prediction"], type=Subsection.Types.SKILL),
        Subsection("Knowledge-based Artificial Intelligence", elements=["Semantic networks", "Generate and test", "Means-ends analysis", "Production Systems", "Case-based reasoning", "Representation concepts like frames or scripts", "Leveraging context", "constraints", "and primitive concepts to contain combinatorial explosion", "Classification", "Diagnosis", "Meta-reasoning"], type=Subsection.Types.SKILL),
        Subsection("Reinforcement Learning", elements=["Markov decision process", "Temporal difference learning", "Policy/value iteration"], type=Subsection.Types.SKILL),
        Subsection("Machine Learning", elements=["Supervised Learning (e.g. Neural Networks", "Support Vector Machines", "K-Nearest Neighbors)", "Optimizers (e.g. Random Hill Climb", "Annealing", "Genetic", "and MIMIC)", "Unsupervised Learning (e.g. K-Means", "Expectation Maximization)", "Dimensionality Reduction (e.g. Random Projection", "Independent Component Analysis", "Principal Component Analysis", "Linear Discriminant Analysis) "], type=Subsection.Types.SKILL),
        Subsection("Deep Learning", elements=["Regularization", "Hyper-parameter Tuning", "Model Topology", "Convolutional Neural Networks", "Addressing Data Bias", "Recurrent Neural Network", "Long Short-Term Memory", "Attention", "Transformers", "Generative Adversarial Networks"], type=Subsection.Types.SKILL),
        Subsection("Algorithms", elements=["Runtime Analysis", "Dynamic Programming", "Divide an Conquer", "Graphs", "Flow", "RSA", "Modular Arithmetic", "Linear Programming"], type=Subsection.Types.SKILL),
    ], type=Subsection.Types.SKILL))

    a=0