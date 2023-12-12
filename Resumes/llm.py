import google.generativeai as palm

class LLM:
    def __init__(self, api_key) -> None:
        palm.configure(api_key=api_key)
        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        self.model = models[0]
        self.model.output_token_limit = 4096

    def getTips(self, resume, jobDesc):
        prompt = '''Please review the following resume and job description, both labeled and contained in brackets below. For the 'Projects' and 'Work Experience' sections, please rewrite each bullet from the resume, as if you were me, with the intent to incorporate the most important terms and concepts from the job description, or otherwise suggest removing the bullet if it is irrelevant. These rewrites should be provided as part of a table, which will also include the bullet as it existed originally, and the reason for the rewrite (either the term or concept identified in the job description, or irrelevancy). Then, after the table, for the 'Skills' section, select and list the top 10-20 comma separated values of the section relevant to the job.'''
        prompt = "{}\n\nResume:{{{}}}\n\nJob Description:{{{}}}".format(prompt, resume, jobDesc)

        resp = palm.generate_text(model=self.model, prompt=prompt, max_output_tokens=4096)
        return resp.result



# Resume:{Mark Zimmerman

# Mzimm003@gmail.com – Cell: (916) 662-6126 – Torrance, CA – https://www.linkedin.com/in/mark-zimmerman-122b1a60/



# Projects:


# GEORGIA INSTITUTE OF TECHNOLOGY

# Atlanta, GA

# Aug 2021 – Present



#   Object Detection on BDD100k dataset

# -Implemented DINO (DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection).

# -Coordinated with a team to support DINO implementation with Classification backbones (EfficientNet and ResNeSt).

# -Collaborated to solve problems of training limitations (e.g. memory and compute time limitations), diagnostics (e.g. deep learning model information propagation), and performance.

#   OpenAI’s Gym based Football Game

# -Implemented the training pipeline of a Multi-agent reinforcement learning environment.

# -Documented an ablation study integrating concepts of COMA (Counterfactual Multi-Agent) methods with PPO (Proximal Policy Optimization).

#   OpenAI’s Gym based Lunar Lander

# -Implemented the policy infrastructure for a reinforcement learning agent and its training pipeline.

# -Analyzed hyperparameter impact for Q-learning agent with replay memory, using neural net as a Q approximator.

# -Programmed efficient use of hardware including multiprocessing with CPU and committing vectorized environment, replay memory, and neural net training calculations on the GPU.

#   Raven Progressive Matrix Solver

# -Built a Knowledge-based artificial intelligence agent.

# -Evaluated techniques of computer vision, statistics, ensemble learning, and metacognition for their ability to rival human capability in pattern recognition.


# Work Experience:


# UNIBAIL RODAMCO WESTFIELD

# Los Angeles, CA

# Oct 2013 – Jul 2021



# Senior Recoverable Revenue Accountant | Jan 2017 – Jul 2021

# -Developed tools in excel, leveraging AI and machine learning techniques, to provide for faster, more accurate analysis, review, and calculation processes.

# -Wrote documentation and hosted training to support the utilization of these 10+ tools.

# -Led training for all job facets from the technical to the analytical for 50+ persons since 2017, including new team members, entire departments after reorganization, and contracted parties abroad.

# -Prepared analyses and summaries for upper and executive management to inform multi-million dollar business decisions.

# -Collaborated with IT to develop and test process improvements, reducing manual workloads by 100+ hours.

# -Oversaw cycle work done for 40+ properties and 1,000s of abstractions of tenant agreements into JD Edwards E1 performed by junior team members.


# Recoverable Revenue Accountant | May 2015 – Dec 2016

# -Abstracted, and maintained, the appropriate expense recovery terms into JD Edwards E1 from dozens of tenant agreement forms (lease, amendment, easement, etc.) for 1,000s of tenants.

# -Reconciled, forecasted, and budgeted recoverable revenues for 1000s of tenants.

# -Supported Accounts Receivable in the resolution of 100s of tenant queries and disputes related to Recoverable Revenues via a JIRA ticketing system.

# -Assisted Center Management, Regional Analyst, Regional Finance Directors, and Shared Services with requests and questions relating to Recoverable Revenues.

# -Identified and implemented process improvements.


# AR Specialist | Oct 2013 – May 2015

# -Maintained 1000s of mall tenants’ ledger’s accuracy through thorough research and analysis.

# -Communicated discrepancies in billings and payments received intelligibly and diplomatically.

# -Collaborated interdepartmentally and with peers to achieve the above for over a thousand tenants at once.


# Education:


# GEORGIA INSTITUTE OF TECHNOLOGY

# Ongoing Master’s in Computer Science - Machine Learning

# Expected graduation: December 2023

# Current GPA: 4.0/4.0

# Atlanta, GA





# EL CAMINO COLLEGE

# Attended Supplementary Computer Science and Technology classes

# Preparation for Master’s program - no credential obtained

# GPA: 4.0/4.0

# Torrance, CA





# UNIVERSITY OF CALIFORNIA, LOS ANGELES EXTENSION

# Completed Certificate of Accounting

# GPA: 3.94/4.0

# Los Angeles, CA





# UNIVERSITY OF CALIFORNIA, RIVERSIDE

# Completed Bachelor of Science in Mathematics

# GPA: 2.78/4.0

# Riverside, CA




# Skills:

# Languages: Python, C++, Java, C#

# Libraries: NumPy, PyTorch, Ray.RLLib, Sklearn, MatPlotLib, Gym, Pandas, Pillow, OpenCV

# Technologies: Visual Studio, VS Code, Git, Anaconda, Docker, Unity, Jupyter Notebooks, CUDA, LaTex, Inkscape, Linux, Windows, Microsoft Office

# Studies:

# Artificial Intelligence: Graph search, Heuristic search, Adversarial search, Bayesian Networks, Markov        Chains, K-means clustering, Decision trees, Ensemble learners, Bagging, Boosting, Gaussian mixture        models, Hidden Markov models

# Game Artificial Intelligence: Pathfinding, Navigation mesh, Fuzzy logic, Procedural content generation,        Finite state machines, Ballistic trajectory prediction

# Knowledge-based Artificial Intelligence: Semantic networks, Generate and test, Means-ends analysis,        Production Systems, Case-based reasoning, Representation concepts like frames or scripts, Leveraging     context, constraints, and primitive concepts to contain combinatorial explosion, Classification,        Diagnosis, Meta-reasoning

# Reinforcement Learning: Markov decision process, Temporal difference learning, Policy/value iteration,

# Machine Learning: Supervised Learning (e.g. Neural Networks, Support Vector Machines, K-Nearest        Neighbors), Optimizers (e.g. Random Hill Climb, Annealing, Genetic, and MIMIC), Unsupervised        Learning (e.g. K-Means, Expectation Maximization), Dimensionality Reduction (e.g. Random        Projection, Independent Component Analysis, Principal Component Analysis, Linear Discriminant        Analysis)

# Deep Learning: Regularization, Hyper-parameter Tuning, Model Topology, Convolutional Neural        Networks, Addressing Data Bias, Recurrent Neural Network, Long Short-Term Memory, Attention,        Transformers, Generative Adversarial Networks

# Algorithms: Runtime Analysis, Dynamic Programming, Divide an Conquer, Graphs, Flow, RSA, Modular        Arithmetic, Linear Programming

# }


# Job description:{Engineering Manager, Sensing & Understanding

# About the Company

# At Torc, we have always believed that autonomous vehicle technology will transform how we travel, move freight, and do business.

# A leader in autonomous driving since 2007, Torc has spent over a decade commercializing our solutions with experienced partners. Now a part of the Daimler family, we are focused solely on developing software for automated trucks to transform how the world moves freight.

# Join us and catapult your career with the company that helped pioneer autonomous technology, and the first AV software company with the vision to partner directly with a truck manufacturer.

# Meet the team:

# The Sensing & Understanding Department develops software that provides a full scene understanding of the world and its constituents to inform desired vehicle behavior. We accomplish this by applying large scale machine learning as well as classical signal processing techniques to analyze our sensor data to create a clear and coherent picture of the current driving situation. To be able to do this, we develop a highly automated, continuous data loop from data selection, to training, to system release in close collaboration with data strategy, infrastructure, simulation, and software integration.

# What you’ll do:

# As an Engineering Manager in the Sensing and Understanding Department, you will manage a team of software engineers focused on software for L4 autonomous trucks. The Engineering Manager is responsible for all people leadership activities for assigned engineers. This includes improving the work execution and quality of their team along with communicating with other teams and management. You will also use technical savvy to collaborate on product development.

# Lead a team of engineers to develop state-of-the-art perception algorithms, ensuring our self-driving vehicles can drive safely and smoothly on the road

# Contribute to the technical decision making and the product roadmap of the team

# Inspire a team that focuses on achieving their project goals, while also creating space for research-driven innovation

# Ensure well designed production software is being delivered to the organization

# Develop your team by focusing on career growth, maintaining a high bar on performance, and facilitating open and respectful communication

# What you’ll need to succeed:

# Bachelor’s degree in Computer Science, Computer Engineering, or engineering equivalent

# Minimum 4+ years' experience leading engineering teams in the delivery of production software solutions that include complex algorithm development and data models

# Applied experience solving state estimation and optimization problems

# Minimum 5 years’ experience writing C++ software on Linux systems

# Deep experience of best practices in software architecture and design

# Exhibit strong facilitation, technical team coaching, systems thinking, and servant leadership skills

# Demonstrated experience managing and growing high performing teams

# Experienced in working with product managers to drive business-level priorities

# Demonstrated experience in data-driven decision making

# Comfortable in a fast-moving organization and able to quickly learn and adapt

# Bonus Points!

# Relevant master's degree or PhD degree

# Processing sensor data such as LIDAR, RADAR, or Camera data

# Experience working on autonomous robot systems

# Perks of Being a Full-time Torc’r

# Torc cares about our team members and we strive to provide benefits and resources to support their health, work/life balance, and future. Our culture is collaborative, energetic, and team focused. Torc offers:

# A competitive compensation package that includes a bonus component and stock options

# 100% paid medical, dental, and vision premiums for full-time employees

# 401K plan with a 6% employer match

# Flexibility in schedule and generous paid vacation (available immediately after start date)

# Company-wide holiday office closures

# AD+D and Life Insurance

# Hiring Range for Job Opening

# US Pay Range

# $160,800—$193,000 USD

# At Torc, we’re committed to building a diverse and inclusive workplace. We celebrate the uniqueness of our Torc’rs and do not discriminate based on race, religion, color, national origin, gender (including pregnancy, childbirth, or related medical conditions), sexual orientation, gender identity, gender expression, age, veteran status, or disabilities.

# Even if you don’t meet 100% of the qualifications listed for this opportunity, we encourage you to apply. We’re always looking for those that are hungry, humble, and people smart and your unique experience may be a great fit for this role or others.}