from Resumes.resume import (
    Resume as Res,
    Section as Sec,
    Subsection as Subsec
)
from pathlib import Path
from pylatex import (
    Document,
    Section,
    Itemize,
    Command,
)
from pylatex.base_classes import (
    Environment,
)
from pylatex.utils import (
    italic,
    bold,
    NoEscape,
)
from pylatex.package import (
    Package
)
import pickle
from typing import List
import datetime


class Resume(Environment):
    content_separator = "\n"

class AdjustWidth(Environment):
    content_separator = "\n"

class Description(Environment):
    content_separator = "\n"

class pdf:
    def __init__(self) -> None:
        self.doc = None

    def fromResume(self, res:Res):
        self.doc = Document(
            Path()/'Resumes/{}/Mark Zimmerman Resume_{}_{}{}'.format(
                datetime.datetime.today().strftime('%m.%y'),
                res.getOrg(),
                res.getJob()[res.getJob().rfind('-'):]),
            fontenc=None,
            inputenc=None,
            lmodern=False,
            textcomp=False,
            page_numbers=False,
            documentclass='res',
            document_options='11pt')
        self.doc.packages.append(Package('hyperref'))
        self.doc.packages.append(Package('changepage'))
        self.doc.preamble.append(Command('hypersetup',['colorlinks=true,urlcolor=blue']))
        self.__createHeader(res)

        with self.doc.create(Resume()):
            for sec in res.sections:
                with self.doc.create(Section(sec.title+':')):
                    self.__createSection(sec)

        self.doc.generate_pdf(clean_tex=False)
        # doc.generate_pdf()

    def __createHeader(self, res:Res):
        self.doc.append(NoEscape(r'\moveleft.5\hoffset\centerline{{\Large\bf {}}}'.format(res.name)))
        # self.doc.append(NoEscape(r'\moveleft.5\hoffset\centerline{{\url{{{}}} --- {} --- {}}}'.format(res.email, res.phone, res.location)))
        self.doc.append(NoEscape(r'\moveleft.5\hoffset\centerline{{\url{{{}}} --- {} --- {} --- \href{{{}}}{{LinkedIn Profile}} --- \href{{{}}}{{GitHub Portfolio}}}}'.format(res.email, res.phone, res.location, res.linkedInLink, res.gitHubLink)))
        # self.doc.append(NoEscape(r'\moveleft.5\hoffset\centerline{{\href{{{}}}{{LinkedIn Profile}} --- \href{{{}}}{{GitHub Portfolio}}}}'.format(res.linkedInLink, res.gitHubLink)))
        self.doc.append(NoEscape(r'\moveleft\hoffset\vbox{\hrule width\resumewidth height 1pt}\smallskip'))

    def __createSection(self, sec:Sec):
        if sec.title in set(['Education','Skills']):
            self.doc.append(Command('vspace*',NoEscape(r'0.03\textwidth')))
        for i, ss in enumerate(sec.content):
            self.__createSubsection(ss)

    def __createSubsection(self, ss:Subsec):
        if ss.type == Subsec.Types.SKILL:
            with self.doc.create(AdjustWidth(arguments=[NoEscape(r'0.05\textwidth'),NoEscape(r'0.0\textwidth')])):
                with self.doc.create(Description()):
                    # self.doc.append(NoEscape(bold(ss.subject+':')))
                    self.doc.append(Command('item',options=ss.subject+':'))
                    if isinstance(ss.elements[0], str):
                        self.__createSubSubsection(ss.elements, sep=',')
                    else:
                        self.__createSubSubsection(ss.elements, sep='\n')
            
        elif ss.type == Subsec.Types.SCHOOL:
            with self.doc.create(AdjustWidth(arguments=[NoEscape(r'0.05\textwidth'),NoEscape(r'0.0\textwidth')])):
            # self.doc.append(Command('vspace*',NoEscape(r'0.01\textwidth')))
            # self.doc.append(Command('hspace*',NoEscape(r'0.05\textwidth')))
            # with self.doc.create(MiniPage(width=NoEscape(r'0.95\textwidth'))):
                header = r'{}\hfill {}'.format(ss.subject, ss.location)
                self.doc.append(NoEscape(header))
                self.__createSubSubsection(ss.elements)
            # self.doc.append(NoEscape(r'\\'))
            
        elif ss.type == Subsec.Types.ORGANIZATION:
            header = ss.subject
            if not ss.startDate is None:
                header = header + r'\hfill {}'.format(ss.startDate.strftime('%b %Y'))
                if not ss.endDate is None:
                    header = header + ' -- {}'.format(ss.endDate.strftime('%b %Y'))
                else:
                    header = header + ' -- Present'
            header += r'\\'
            self.doc.append(NoEscape(header))
            self.doc.append(NoEscape(ss.location))
            self.__createSubSubsection(ss.elements)

    def __createSubSubsection(self, elms:List[Subsec]|List[str], sep='bullet', listVShift=-0.01):
        if isinstance(elms[0], Subsec):
            if sep == '\n':
                self.doc.append(NoEscape(r'\hfill'))
                # self.doc.append(NoEscape(r'\setlist[description]{font=\normalfont\itshape}'))
                with self.doc.create(Description()):
                    for i, e in enumerate(elms):
                        # header = italic(e.subject + ': ')
                        # self.doc.append(NoEscape(header))
                        self.doc.append(Command('item',italic(e.subject+':')))#, NoEscape(r'headstyle=italic')))
                        self.__createSubSubsection(e.elements, ',')
            else:
                for i, e in enumerate(elms):
                    with self.doc.create(AdjustWidth(arguments=[NoEscape(r'0.05\textwidth'),NoEscape(r'0.0\textwidth')])):
                        header = italic(e.subject)
                        if not e.startDate is None:
                            header = header + r' $|$ {}'.format(e.startDate.strftime('%b %Y'))
                            if not e.endDate is None:
                                header = header + ' -- {}'.format(e.endDate.strftime('%b %Y'))
                            else:
                                header = header + ' -- Present'
                        self.doc.append(NoEscape(header))
                        self.__createSubSubsection(e.elements, sep)
        elif isinstance(elms[0], str):
            if sep == 'bullet':
                self.doc.append(Command('vspace*',NoEscape(r'{:f}\textwidth'.format(listVShift))))
                with self.doc.create(Itemize()) as it:
                    self.doc.append(NoEscape(r'\setlength\itemsep{-0.2em}'))
                    for e in elms:
                        it.add_item(e)
            elif sep == ',':
                # with self.doc.create(AdjustWidth(arguments=[NoEscape(r'0.05\textwidth'),NoEscape(r'0.0\textwidth')])):
                    for i, e in enumerate(elms):
                        add = e
                        if i != len(elms)-1:
                            add += ', '
                        self.doc.append(add)

    

def main():
    r = None
    with open('./Resumes/main/resume.pkl','rb') as f:
        r = pickle.load(f)
    pdf().fromResume(r)
# doc.append('Mark')
# with doc.create(Resume()):
#     with doc.create(tx.Section('OBJECTIVE')):
#         doc.append('Stuffffffffffffffffffff')


# from Resumes.resume import (Section as Sec, Subsection as SubSec)
# from Search.resume import (Resume as OldRes, Section as OldSec, Subsection as OldSubSec)

# def reup(r:Res|Sec|Subsec):
#     if isinstance(r, OldRes) or isinstance(r, Res):
#         l = []
#         for s in r.sections:
#             l.append(reup(s))
#         r.sections = l
#         r = Res(**r.__dict__)
#     elif isinstance(r, OldSec) or isinstance(r, Sec):
#         l = []
#         for s in r.content:
#             l.append(reup(s))
#         r.content = l
#         r = Sec(**r.__dict__)
#     elif isinstance(r, OldSubSec) or isinstance(r, Subsec):
#         l = []
#         for s in r.elements:
#             l.append(reup(s))
#         r.elements = l
#         r.type = reup(r.type)
#         # r.startDate = None
#         # r.endDate = None
#         r = Subsec(**r.__dict__)
#     elif isinstance(r, OldSubSec.Types):
#         r = getattr(Subsec.Types,r.name)
#     return r