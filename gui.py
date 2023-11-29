import PySimpleGUI as sg

from Search.transforms import Transform
from Search.profile import (
    Profile,
    Portfolio
)
from Search.search import Search
from Search.utility import request

import pickle
import webbrowser
from pathlib import Path
from typing import (
    List,
    Dict
)
from functools import partial
import enum

class GUI:
    def __init__(self, portfolio:Portfolio) -> None:
        self.windows:Dict[str, sg.Window] = {}
        self.primaryWindow:sg.Window = None
        self.portfolio:Portfolio = portfolio

    def __newWindow(self, name, layout, modal=False, enable_close_attempted_event=False, resizable=False, modalEvents={}, modalCloseSet=set(['OK'])):
        loc = (None, None)
        ret = None
        if self.primaryWindow:
            loc = self.primaryWindow.current_location()
        w = sg.Window(
            name,
            layout,
            modal=modal,
            location=loc,
            enable_close_attempted_event=enable_close_attempted_event,
            resizable=resizable,
            finalize=True)
        if modal:
            while True:
                e, v = w.read()
                if e in modalEvents:
                    ret = modalEvents[e](w,e,v)
                if e in modalCloseSet or e == sg.WIN_CLOSED:
                    break
            w.close()
            return ret
        else:
            return w
    
    def __closeWindow(self, w:sg.Window):
        del self.windows[w]
        w.close()
    
    def closeAllWindows(self):
        wins = list(self.windows.keys())
        for w in wins:
            self.__closeWindow(w)

    MAINWINDOWNAME = "Work"
    NEWPROFILE = '--New--'
    class MAINELEMENTS(enum.Enum):
        PROFILES = enum.auto()
        JOBSDETAIL = enum.auto()
        ALLNEWJOBS = enum.auto()
        NEWJOBS = enum.auto()
        OPENPROFILE = enum.auto()
    @staticmethod
    def MAINWINDOWLAYOUT(profiles):
        profile_panel_layout = sg.Col([
            [sg.Text("Profiles")], 
            [sg.Listbox([k for k in profiles.keys()], expand_x=True, expand_y=True, key=GUI.MAINELEMENTS.PROFILES)],
            [sg.Button('Access Profile', key=GUI.MAINELEMENTS.OPENPROFILE)]
            ], expand_x=True, expand_y=True)
        jobs_panel_layout = sg.Col([
            [sg.Text("Jobs")],
            [sg.vtop(sg.Button('Detail', key=GUI.MAINELEMENTS.JOBSDETAIL)),
             sg.Col([[sg.Button('Get All New Jobs', key=GUI.MAINELEMENTS.ALLNEWJOBS)],
                     [sg.Multiline(size=(100,50), key=GUI.MAINELEMENTS.NEWJOBS)]], pad=((0,0),(0,1)))],
            ], expand_x=True, expand_y=True)

        layout_l = [[profile_panel_layout]]
        layout_c = [[]]
        layout_r = [[jobs_panel_layout]]

        return [
            [
                sg.Col(layout_l, expand_x=True, expand_y=True),
                sg.Col(layout_r, expand_x=True, expand_y=True)
            ]
        ]
    
    def mainWindow(self):
        w = self.__newWindow(GUI.MAINWINDOWNAME, GUI.MAINWINDOWLAYOUT(self.portfolio.profiles), enable_close_attempted_event=True, resizable=True)
        w.maximize()
        self.primaryWindow = w
        self.windows[w] = {
            GUI.MAINELEMENTS.OPENPROFILE:self.openProfile,
            sg.WIN_X_EVENT:self.endProgram,
            GUI.MAINELEMENTS.JOBSDETAIL:self.openJobs,
            GUI.MAINELEMENTS.ALLNEWJOBS:... #TODO
            }
    
    def openProfile(self, values):
        for p in values[GUI.MAINELEMENTS.PROFILES]:
            w = self.profileWindow(p)
            self.refreshSearchConfigVisual(w, self.portfolio.profiles[p])

    def openJobs(self, values):
        w = self.jobsWindow()
    
    def endProgram(self, values):
        lyt = [
            [sg.Text('Save Work?')],
            [sg.Button("Yes"),sg.Button("No")]
            ]
        save_window = sg.Window("Save?", lyt, modal=True, location=self.primaryWindow.current_location())
        while True:
            e, v = save_window.read()
            if e == "Yes":
                with open("Search/profiles.pkl", "wb") as f:
                    pickle.dump(self.portfolio, f)
                break
            if e == "No" or e == sg.WIN_CLOSED:
                break
        save_window.close()
        return 'CLOSEALL'

    class PROFILEELEMENTS(enum.Enum):
        PEEKLINKS = enum.auto()
        ADDSEARCH = enum.auto()
        COMMITPHRASES = enum.auto()
        MLSEARCHHEADER = enum.auto()
        LINKS = enum.auto()
        DESCRIPTION = enum.auto()
        PEEKDESC = enum.auto()
        JOBKEYID = enum.auto()
        PAGEKEYID = enum.auto()
        HTMLKEY = enum.auto()
        SEARCHPHRASES = enum.auto()
        JOBSTATUSUPDATE = enum.auto()
        GETCURRENTJOBS = enum.auto()
        JOBSDETAIL = enum.auto()
    @staticmethod
    def PROFILESWINDOWLAYOUT():
        header_panel_layout = sg.Col([
            [sg.Text("Sample Header")],
            [sg.Multiline(key=GUI.PROFILEELEMENTS.MLSEARCHHEADER, size=(60,20), expand_x=True, expand_y=True)],
            ], expand_x=True, expand_y=True)
        link_peek_layout = sg.Col([
            [sg.Text("Job Identifying Keyword Help")],
            [sg.Listbox([], expand_x=True, expand_y=True, key=GUI.PROFILEELEMENTS.LINKS)],
            [sg.Button('Peek Links', key=GUI.PROFILEELEMENTS.PEEKLINKS)]
            ], expand_x=True, expand_y=True)
        search_spec_layout = sg.Col([
            [sg.Col([[sg.Text("Link Keyword Identifying Jobs")],
                     [sg.Text("Link Keyword Identifying Pages")],
                     [sg.Text("Job Desc HTML Element")]]),
             sg.Col([[sg.In(key=GUI.PROFILEELEMENTS.JOBKEYID, expand_x=True)],
                     [sg.In(key=GUI.PROFILEELEMENTS.PAGEKEYID, default_text='page', expand_x=True)],
                     [sg.In(key=GUI.PROFILEELEMENTS.HTMLKEY, default_text='type.class; e.g. article.node--type-job-opportunity', expand_x=True)],
                     ])],
            ], expand_x=True, expand_y=True)
        search_phrase_layout = sg.Col([
            [sg.Multiline(size=(25,8), key=GUI.PROFILEELEMENTS.SEARCHPHRASES),sg.Button('Commit Phrases', key=GUI.PROFILEELEMENTS.COMMITPHRASES)],
            ], expand_x=True, expand_y=True)
        desc_peek_layout = sg.Col([
            [sg.Text("Job Desc HTML Element Help")],
            [sg.Multiline('', expand_x=True, expand_y=True, key=GUI.PROFILEELEMENTS.DESCRIPTION)],
            [sg.Button('Peek Description', key=GUI.PROFILEELEMENTS.PEEKDESC)]
            ], expand_x=True, expand_y=True)
        search_panel_layout = [
            [header_panel_layout, link_peek_layout, desc_peek_layout],
            [search_spec_layout],
            [sg.Button('Commit Search', key=GUI.PROFILEELEMENTS.ADDSEARCH)],
            [search_phrase_layout]
            ]
        
        job_panel_layout = [
            [sg.Button('Find Current Jobs', key=GUI.PROFILEELEMENTS.GETCURRENTJOBS)],
            [sg.Multiline(size=(70,20),key=GUI.PROFILEELEMENTS.JOBSTATUSUPDATE)],
            [sg.Button('View Jobs', key=GUI.PROFILEELEMENTS.JOBSDETAIL)]
        ]

        tabs = sg.TabGroup([[
            sg.Tab('Search Config', search_panel_layout),
            sg.Tab('Jobs', job_panel_layout)]], expand_x=True, expand_y=True)

        return [
            [
                tabs
            ]
        ]
            
    def profileWindow(self, profile:str):
        w = self.__newWindow(profile, GUI.PROFILESWINDOWLAYOUT(), resizable=True)
        self.windows[w] = {
            GUI.PROFILEELEMENTS.ADDSEARCH:partial(self.addSearch, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PROFILEELEMENTS.PEEKLINKS:partial(self.peekLinks, window=w),
            GUI.PROFILEELEMENTS.COMMITPHRASES:partial(self.commitPhrases, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PROFILEELEMENTS.GETCURRENTJOBS:partial(self.getCurrentJobs, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PROFILEELEMENTS.JOBSDETAIL:partial(self.openJobDetail, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PROFILEELEMENTS.PEEKDESC:partial(self.peekDesc, window=w, profile=self.portfolio.profiles[profile]),
            }
        return w

    def peekDesc(self, values, window:sg.Window, profile:Profile):
        if profile.search.searchReq is None:
            self.errorMsg("Must first commit search to create profile.")
        else:
            window[GUI.PROFILEELEMENTS.DESCRIPTION].update(value=profile.samplePosts())

    def openJobDetail(self, values, window:sg.Window, profile:Profile):
        self.jobsWindow(profile.name)

    def getCurrentJobs(self, values, window:sg.Window, profile:Profile):
        self.portfolio.getNewJobsByProfile(profile)
        window[GUI.PROFILEELEMENTS.JOBSTATUSUPDATE].update('{} new jobs found:\n{}'.format(len(profile.currentPosts), '\n'.join(profile.currentPosts.keys())))

    def commitPhrases(self, values, window:sg.Window, profile:Profile):
        srchPhrss = values[GUI.PROFILEELEMENTS.SEARCHPHRASES].split('\n')
        profile.search.setSearchPhrases(srchPhrss)
        window[GUI.PROFILEELEMENTS.SEARCHPHRASES].update('\n'.join(profile.search.searchPhrases))

    def searchPhraseWindow(self, search):
        CNFBTTN = 'Confirm'
        SRCH = 'SEARCH'
        lyt = [
            [sg.Text('Please highlight and confirm the\nsearch phrase in the url:')],
            [sg.Multiline(search, key=SRCH, size=(100,20)), sg.Button(CNFBTTN)]
        ]
        modEv = {
            CNFBTTN:lambda w,e,v:w[SRCH].Widget.selection_get()
        }
        selection = self.__newWindow('Search Phrase',lyt,modal=True, modalEvents=modEv, modalCloseSet=set([CNFBTTN]))
        return selection
        
    def peekLinks(self, values, window:sg.Window):
        if values[GUI.PROFILEELEMENTS.MLSEARCHHEADER] == '':
            self.errorMsg("Must fill the search parameter 'Header'")
        else:
            search_header = Transform().GUIRequestHeaderToRequestParamDict(values[GUI.PROFILEELEMENTS.MLSEARCHHEADER])
            search = request(searchReq=search_header)
            window[GUI.PROFILEELEMENTS.LINKS].update([l for l in search.html.links])

    def addSearch(self, values, window:sg.Window, profile:Profile):
        if profile.name == GUI.NEWPROFILE and '' in {values[GUI.PROFILEELEMENTS.MLSEARCHHEADER],
                  values[GUI.PROFILEELEMENTS.JOBKEYID],
                  values[GUI.PROFILEELEMENTS.PAGEKEYID],
                  values[GUI.PROFILEELEMENTS.HTMLKEY]}:
            self.errorMsg("Must fill the search parameters:\n\t\u2022'Header'\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        elif '' in {values[GUI.PROFILEELEMENTS.JOBKEYID],
                  values[GUI.PROFILEELEMENTS.PAGEKEYID],
                  values[GUI.PROFILEELEMENTS.HTMLKEY]}:
            self.errorMsg("Must fill the search parameters:\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        else:
            if '' == values[GUI.PROFILEELEMENTS.MLSEARCHHEADER]:
                profile.search.setJobKeyId(values[GUI.PROFILEELEMENTS.JOBKEYID])
                profile.search.setPageKeyId(values[GUI.PROFILEELEMENTS.PAGEKEYID])
                profile.search.setDescKey(values[GUI.PROFILEELEMENTS.HTMLKEY])
            else:
                search_header = Transform().GUIRequestHeaderToRequestParamDict(values[GUI.PROFILEELEMENTS.MLSEARCHHEADER])
                srchPhrs = self.searchPhraseWindow(values[GUI.PROFILEELEMENTS.MLSEARCHHEADER])
                search_header['url'] = search_header['url'].replace(srchPhrs, '{}')
                search = Search.byHTML(searchReq=search_header,
                                    jobKeyId=values[GUI.PROFILEELEMENTS.JOBKEYID],
                                    pageKeyId=values[GUI.PROFILEELEMENTS.PAGEKEYID],
                                    descKey=values[GUI.PROFILEELEMENTS.HTMLKEY])
                search.addSearchPhrase(Transform.HTMLTextToPlain(srchPhrs))
                if profile.name != GUI.NEWPROFILE:
                    profile.defineSearch(search)
                else:
                    profile = Profile.bySearch(search)
                    self.portfolio.addProfile(profile)
                    self.primaryWindow[GUI.MAINELEMENTS.PROFILES].update([k for k in self.portfolio.profiles.keys()])
                    tmpwin = self.profileWindow(profile.name)
                    self.__closeWindow(window)
                    window = tmpwin
            self.refreshSearchConfigVisual(window, profile)
    
    def refreshSearchConfigVisual(self, window:sg.Window, profile:Profile):
        window[GUI.PROFILEELEMENTS.JOBKEYID].update(profile.search.jobKeyId)
        window[GUI.PROFILEELEMENTS.PAGEKEYID].update(profile.search.pageKeyId)
        window[GUI.PROFILEELEMENTS.HTMLKEY].update(profile.search.descKey)
        window[GUI.PROFILEELEMENTS.SEARCHPHRASES].update('\n'.join(profile.search.searchPhrases))

    def errorMsg(self, message):
        lyt = [
            [sg.Text(message)],
            [sg.Button("OK")]
            ]
        self.__newWindow("Error", lyt, modal=True)
    
    class JOBELEMENTS(enum.Enum):
        VIEWSITE = enum.auto()
        APPLIED = enum.auto()
        IGNORE = enum.auto()
        GETTIPS = enum.auto()
        UPDATERESUME = enum.auto()
        FILTER = enum.auto()
        JOBLIST = enum.auto()
        JOBDESC = enum.auto()
    class JOBLISTHEADINGS(enum.Enum):
        Job = enum.auto()
        Status = enum.auto()
    @staticmethod
    def JOBSWINDOWLAYOUT(profiles:List[str], default_prof:str):
        job_list_panel_layout = sg.Col([
            [sg.Text("Job List")],
            [sg.Text('Company Filter'), sg.Combo(['',*[p for p in profiles]], default_prof, enable_events=True, key=GUI.JOBELEMENTS.FILTER)],
            [sg.Table([[]], headings=[x.name for x in GUI.JOBLISTHEADINGS], key=GUI.JOBELEMENTS.JOBLIST, enable_events=True, expand_x=True, expand_y=True)],
            ], expand_x=True, expand_y=True)
        job_desc_layout = sg.Col([
            [sg.Text("Description")],
            [sg.Multiline(key=GUI.JOBELEMENTS.JOBDESC, expand_x=True, expand_y=True)],
            [sg.Button('View Website', key=GUI.JOBELEMENTS.VIEWSITE)],
            [sg.Button('Applied', key=GUI.JOBELEMENTS.APPLIED),sg.Button('Ignore', key=GUI.JOBELEMENTS.IGNORE)],
            ], expand_x=True, expand_y=True)
        GPT_layout = sg.Col([
            [sg.Text("LLM Tips")],
            [sg.Multiline(expand_x=True, expand_y=True)],
            [sg.Button('Get Tips', key=GUI.JOBELEMENTS.GETTIPS)],
            ], expand_x=True, expand_y=True)
        resume_layout = sg.Col([
            [sg.Text("Resume Changes")],
            [sg.Multiline(expand_x=True, expand_y=True)],
            [sg.Button('Update Resume', key=GUI.JOBELEMENTS.UPDATERESUME)],
            ], expand_x=True, expand_y=True)
        
        layout_l = [[job_list_panel_layout]]
        layout_c = [[job_desc_layout]]
        layout_r = [[GPT_layout],[resume_layout]]

        return [
            [
                sg.Col(layout_l, expand_x=True, expand_y=True),
                sg.Col(layout_c, expand_x=True, expand_y=True),
                sg.Col(layout_r, expand_x=True, expand_y=True),
            ]
        ]
            
    def jobsWindow(self, filt=''):
        w = self.__newWindow("Jobs", GUI.JOBSWINDOWLAYOUT([p for p in self.portfolio.profiles if p != GUI.NEWPROFILE] ,filt), resizable=True)
        w[GUI.JOBELEMENTS.FILTER].update(value=filt)
        self.refreshJobList({GUI.JOBELEMENTS.FILTER:filt},w)
        self.windows[w] = {
            GUI.JOBELEMENTS.FILTER:partial(self.refreshJobList, window=w),
            GUI.JOBELEMENTS.APPLIED:partial(self.setJobAsApplied, window=w),
            GUI.JOBELEMENTS.IGNORE:partial(self.setJobAsIgnore, window=w),
            GUI.JOBELEMENTS.JOBLIST:partial(self.displayJobDesc, window=w),
            GUI.JOBELEMENTS.VIEWSITE:partial(self.viewWebsite, window=w),
            GUI.JOBELEMENTS.GETTIPS:...,#TODO
            GUI.JOBELEMENTS.UPDATERESUME:...,#TODO
            }
        return w
    
    def viewWebsite(self, values, window:sg.Window):
        jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
        for v in values[GUI.JOBELEMENTS.JOBLIST]:
            webbrowser.open(self.portfolio.historicalPosts[jobs[v][GUI.JOBLISTHEADINGS.Job.value-1]].link)
    
    def displayJobDesc(self, values, window:sg.Window):
        if values[GUI.JOBELEMENTS.JOBLIST]:
            jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
            dispJob = jobs[values[GUI.JOBELEMENTS.JOBLIST][0]][GUI.JOBLISTHEADINGS.Job.value-1]
            window[GUI.JOBELEMENTS.JOBDESC].update(value=self.portfolio.historicalPosts[dispJob].desc)
    
    def setJobAsApplied(self, values, window:sg.Window):
        jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
        for v in values[GUI.JOBELEMENTS.JOBLIST]:
            self.portfolio.historicalPosts[jobs[v][GUI.JOBLISTHEADINGS.Job.value-1]].toggleApplied()
        self.refreshJobList(values, window)

    def setJobAsIgnore(self, values, window:sg.Window):
        jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
        for v in values[GUI.JOBELEMENTS.JOBLIST]:
            self.portfolio.historicalPosts[jobs[v][GUI.JOBLISTHEADINGS.Job.value-1]].toggleIgnore()
        self.refreshJobList(values, window)

    def refreshJobList(self, values, window:sg.Window):
        def filt(k):
            return values[GUI.JOBELEMENTS.FILTER] == '' or values[GUI.JOBELEMENTS.FILTER] in k[GUI.JOBLISTHEADINGS.Job.value-1]
        tableDict = filter(filt, self.portfolio.historicalPosts.items())
        currentSelection = set()
        if GUI.JOBELEMENTS.JOBLIST in values:
            currentSelection = window[GUI.JOBELEMENTS.JOBLIST].get()
            currentSelection = set(currentSelection[x][GUI.JOBLISTHEADINGS.Job.value-1] for x in values[GUI.JOBELEMENTS.JOBLIST])
        newSelection = []
        table = []
        for i, (j, p) in enumerate(tableDict):
            table.append([j, p.getStatus()])
            if j in currentSelection:
                newSelection.append(i)
        window[GUI.JOBELEMENTS.JOBLIST].update(values=table, select_rows=newSelection)

    def run(self):
        # Create an event loop
        keepOpen = True
        while keepOpen:
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


            # elif event == GUI.JOBSDETAIL:
            #     jobs_window = sg.Window("Jobs", JOBSWINDOWLAYOUT(), modal=True, location=window.current_location())
            #     while True:
            #         e, v = jobs_window.read()
            #         # if e == "Yes":
            #         #     with open("Search/profiles.pkl", "wb") as f:
            #         #         pickle.dump(profiles, f)
            #         #     break
            #         if e == "No" or e == sg.WIN_CLOSED:
            #             break
            #     jobs_window.close()
            # elif event == GUI.ALLNEWJOBS:
            #     for p in values['PROFILES']:
            #         profileWindow(window, p)


            if result == 'CLOSEALL':
                keepOpen = False
                self.closeAllWindows()

def main():
    port:Portfolio = Portfolio()
    port.addProfile(Profile(GUI.NEWPROFILE, Search(descKey='type.class; e.g. article.node--type-job-opportunity')))
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            port = pickle.load(f)
    gui = GUI(portfolio=port)

    gui.mainWindow()

    gui.run()

if __name__ == "__main__":
    main()