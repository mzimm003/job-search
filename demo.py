import gui
import pickle
import traceback
import PySimpleGUI as sg
import enum
from Resumes.resume import Resume, Subsection
from typing import List



class GUI2(gui.GUI):
    class RESUMEELEMENTS(enum.Enum):
        EXPERIENCE = enum.auto()
        EXPKEEP = enum.auto()
        EXPREVISION = enum.auto()
        SKILL = enum.auto()
        SKLKEEP = enum.auto()
        SKLREVISION = enum.auto()
        AIEXP = enum.auto()
        AISKILL = enum.auto()
        RUNAI = enum.auto()
        SAVEJSON = enum.auto()
        SAVEPDF = enum.auto()
    @staticmethod
    def RESUMEWINDOWLAYOUT(resume:Resume):
        class KeyCount:
            def __init__(self) -> None:
                self.counts = {k:0 for k in GUI2.RESUMEELEMENTS}
            def getKey(self, k):
                ret = self.counts[k]
                self.counts[k] += 1
                return (k, ret)
        exp_col_sizes = [(70,None),(5,1),(70,None),(70,None)]
        label_col_sizes = [(70,1),(5,1),(70,1),(70,1)]
        def addContent(l:List, subsecs:List[Subsection]):            
            for ss in subsecs:
                if ss.getType() == Subsection.Types.ORGANIZATION:
                    l.append([sg.Text(ss.getSubject(), size=label_col_sizes[0]),
                              sg.Text("", size=label_col_sizes[1]),
                              sg.Text("", size=label_col_sizes[2]),
                              sg.Text("", size=label_col_sizes[3]),
                              ])
                    addContent(l, ss.elements)
                elif (ss.getType() == Subsection.Types.POSITION or
                      ss.getType() == Subsection.Types.PROJECT or
                      ss.getType() == Subsection.Types.SCHOOL):
                    l.append([sg.Text('\t'+ss.getSubject(), size=label_col_sizes[0]),
                              sg.Text("", size=label_col_sizes[1]),
                              sg.Text("", size=label_col_sizes[2]),
                              sg.Text("", size=label_col_sizes[3]),])
                    ##MAYBE##
                    l.append([
                        sg.Table([[e] for e in ss.getElements()], key=keys.getKey(GUI2.RESUMEELEMENTS.EXPERIENCE), size=exp_col_sizes[0]),
                        sg.Col([[sg.Checkbox('', default=True, key=keys.getKey(GUI2.RESUMEELEMENTS.EXPKEEP), size=exp_col_sizes[1])] for e in ss.getElements()]),
                        sg.Table([[e] for e in ss.getElements()], key=keys.getKey(GUI2.RESUMEELEMENTS.EXPREVISION), size=exp_col_sizes[2]),
                        sg.Table([[] for e in ss.getElements()], key=keys.getKey(GUI2.RESUMEELEMENTS.AIEXP), size=exp_col_sizes[3])
                    ])
                    #########
                    # for e in ss.getElements():
                    #     l.append([sg.Multiline(e, key=keys.getKey(GUI2.RESUMEELEMENTS.EXPERIENCE), size=exp_col_sizes[0]),
                    #               sg.Checkbox('', default=True, key=keys.getKey(GUI2.RESUMEELEMENTS.EXPKEEP), size=exp_col_sizes[1]),
                    #               sg.Multiline(e, key=keys.getKey(GUI2.RESUMEELEMENTS.EXPREVISION), size=exp_col_sizes[2]),
                    #               sg.Multiline("", key=keys.getKey(GUI2.RESUMEELEMENTS.AIEXP), size=exp_col_sizes[3]),])
                elif ss.getType() == Subsection.Types.SKILL:
                    l.append([sg.Text(ss.getSubject(), size=label_col_sizes[0]),
                              sg.Text("", size=label_col_sizes[1]),
                              sg.Text("", size=label_col_sizes[2]),
                              sg.Text("", size=label_col_sizes[3]),
                              ])
                    if isinstance(ss.getElements()[0], str):
                        l.append([sg.Multiline(','.join(ss.getElements()), key=keys.getKey(GUI2.RESUMEELEMENTS.SKILL), size=exp_col_sizes[0]),
                                    sg.Checkbox('', default=True, key=keys.getKey(GUI2.RESUMEELEMENTS.SKLKEEP), size=exp_col_sizes[1]),
                                    sg.Multiline(','.join(ss.getElements()), key=keys.getKey(GUI2.RESUMEELEMENTS.SKLREVISION), size=exp_col_sizes[2]),
                                    sg.Multiline("", key=keys.getKey(GUI2.RESUMEELEMENTS.AISKILL), size=exp_col_sizes[3]),])
                    else:
                        for sss in ss.getElements():
                            l.append([sg.Text('\t'+sss.getSubject(), size=label_col_sizes[0]),
                                    sg.Text("", size=label_col_sizes[1]),
                                    sg.Text("", size=label_col_sizes[2]),
                                    sg.Text("", size=label_col_sizes[3]),
                                    ])
                            l.append([sg.Multiline(','.join(sss.getElements()), key=keys.getKey(GUI2.RESUMEELEMENTS.SKILL), size=exp_col_sizes[0]),
                                    sg.Checkbox('', default=True, key=keys.getKey(GUI2.RESUMEELEMENTS.SKLKEEP), size=exp_col_sizes[1]),
                                    sg.Multiline(','.join(sss.getElements()), key=keys.getKey(GUI2.RESUMEELEMENTS.SKLREVISION), size=exp_col_sizes[2]),
                                    sg.Multiline("", key=keys.getKey(GUI2.RESUMEELEMENTS.AISKILL), size=exp_col_sizes[3]),])

        keys = KeyCount()
        org_resume_layout = []
        for sec in resume.getSections():
            org_resume_layout.append([sg.Text(sec.getTitle(), size=label_col_sizes[0]),
                                      sg.Text("", size=label_col_sizes[1]),
                                      sg.Text("", size=label_col_sizes[2]),
                                      sg.Text("", size=label_col_sizes[3]),
                                      ])
            addContent(org_resume_layout, sec.getContent())
        org_resume_layout = sg.Col([
            [sg.Text("", size=label_col_sizes[0]),
             sg.Text("", size=label_col_sizes[1]),
             sg.Text("", size=label_col_sizes[2]),
             sg.Button("Get AI Tips",key=GUI2.RESUMEELEMENTS.RUNAI, size=label_col_sizes[3])],
            [sg.Text("Resume", size=label_col_sizes[0], justification='center'),
             sg.Text("Keep", size=label_col_sizes[1], justification='center'),
             sg.Text("Revisions", size=label_col_sizes[2], justification='center'),
             sg.Text("Rating and Keywords", size=label_col_sizes[3], justification='center')],
            ] + org_resume_layout,
            expand_x=True,
            expand_y=True,
            scrollable=True,
            vertical_scroll_only=True,
            justification='center',
            size=(700, 200))

        return [
            [org_resume_layout],
            [sg.Button('Update Resume', key=GUI2.RESUMEELEMENTS.SAVEJSON),
            sg.Button('Generate PDF', key=GUI2.RESUMEELEMENTS.SAVEPDF)]
        ]
        

    def resumeWindow(self, job, resume):
        lyt = GUI2.RESUMEWINDOWLAYOUT(resume)
        w = self._GUI__newWindow("Resume - {}".format(job), lyt, resizable=True)
        self.windows[w] = {
            # GUI.RESUMEELEMENTS.FILTER:partial(self.refreshJobList, window=w),
            }
        return w
    
    def __closeWindow(self, w:sg.Window):
        del self.windows[w]
        w.close()

    def run(self):
        # Create an event loop
        keepOpen = True
        while keepOpen:
            try:
                window, event, values = sg.read_all_windows()
                result = None
                if event == sg.WIN_CLOSED:
                    if window is self.primaryWindow:
                        result = self.endProgram(values)
                    else:
                        self.__closeWindow(window)
                else:
                    if event in self.windows[window]:
                        result = self.windows[window][event](values)
            except Exception as inst:
                self.errorMsg('{}:{}\n{}'.format(type(inst), inst, traceback.format_exc()))


            if result == 'CLOSEALL':
                keepOpen = False
                self.closeAllWindows()

g = GUI2()
r = None
with open('./Resumes/main/resume.pkl','rb') as f:
    r = pickle.load(f)
w = g.resumeWindow('test', r)
g.run()