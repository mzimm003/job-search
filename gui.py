import PySimpleGUI as sg
import argparse

from Search.transforms import Transform, Request
from Search.profile import (
    Profile,
    Portfolio
)
from Search.search import Search
from Resumes.resume import Resume, Subsection, ResumeRevision
from Resumes.llm import LLM

import pickle
import webbrowser
from pathlib import Path
from typing import (
    List,
    Dict,
)
from functools import partial
import traceback
import enum
import tkinter

class GUI:
    def __init__(self, portfolio:Portfolio=None, llm:LLM=None) -> None:
        self.windows:Dict[str, sg.Window] = {}
        self.primaryWindow:sg.Window = None
        self.portfolio:Portfolio = portfolio
        self.llm:LLM = llm
        

    def __newWindow(self, name, layout, modal=False, enable_close_attempted_event=False, resizable=False, modalEvents={}, modalCloseSet=set(['OK']), loc = (None,None)):
        ret = None
        if loc is None and self.primaryWindow:
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
        # w.maximize()
        self.primaryWindow = w
        self.windows[w] = {
            GUI.MAINELEMENTS.OPENPROFILE:self.openProfile,
            sg.WIN_X_EVENT:self.endProgram,
            GUI.MAINELEMENTS.JOBSDETAIL:self.openJobs,
            GUI.MAINELEMENTS.ALLNEWJOBS:partial(self.getAllNewJobs, window=w),
            }
    
    def getAllNewJobs(self, values, window:sg.Window):
        windowUpdate = ''
        numNewJobs = 0 
        for n, p in self.portfolio.profiles.items():
            self.getCurrentJobs(values=values, window=None, profile=p, updateProfWin=False)
            numNewJobs += len(p.currentPosts)
            windowUpdate += '\n{}:\n\t'.format(p.name)
            windowUpdate += '\n\t'.join(p.currentPosts.keys())
        window[GUI.MAINELEMENTS.NEWJOBS].update('{} new jobs found:{}'.format(numNewJobs, windowUpdate))

    def openProfile(self, values):
        for p in values[GUI.MAINELEMENTS.PROFILES]:
            w = self.profileWindow(p)
            if p != GUI.NEWPROFILE:
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
        #Config Elements
        PEEKLINKS = enum.auto()
        ADDSEARCH = enum.auto()
        COMMITPHRASES = enum.auto()
        MLSEARCHHEADER = enum.auto()
        SEARCHRETTYPE = enum.auto()
        SEARCHRETTYPESHTML = enum.auto()
        SEARCHRETTYPESJSON = enum.auto()
        DESCRETTYPE = enum.auto()
        DESCRETTYPESHTML = enum.auto()
        DESCRETTYPESJSON = enum.auto()
        SEARCHRENREQ = enum.auto()
        SEARCHRENREQNO = enum.auto()
        SEARCHRENREQYES = enum.auto()
        DESCRENREQ = enum.auto()
        DESCRENREQNO = enum.auto()
        DESCRENREQYES = enum.auto()
        LINKS = enum.auto()
        DESCRIPTION = enum.auto()
        PEEKDESC = enum.auto()
        JOBKEYID = enum.auto()
        PAGEKEYID = enum.auto()
        HTMLTITLEKEY = enum.auto()
        HTMLDESCKEY = enum.auto()
        SEARCHPHRASES = enum.auto()
        METHOD = enum.auto()
        METHUP = enum.auto()
        METHDOWN = enum.auto()
        CSSSELECTORHELP = enum.auto()
        CSSSELECTORHELP1 = enum.auto()
        PROFILENAME = enum.auto()

        #Job Elements
        JOBSTATUSUPDATE = enum.auto()
        GETCURRENTJOBS = enum.auto()
        JOBSDETAIL = enum.auto()
    @staticmethod
    def PROFILESWINDOWLAYOUT():
        #CONFIGURATION LAYOUT
        header_panel_layout = sg.Col([
            [sg.Text("Profile Name:"),sg.In(key=GUI.PROFILEELEMENTS.PROFILENAME, expand_x=True)],
            [sg.Text("Sample Request")],
            [sg.Multiline(key=GUI.PROFILEELEMENTS.MLSEARCHHEADER, size=(50,20), expand_x=True, expand_y=True)],
            ], expand_x=True, expand_y=True)
        search_spec_layout = sg.Col([
            [sg.Col([[sg.Text("Link Keyword Identifying Jobs")],
                     [sg.Text("Link Keyword Identifying Pages")],
                     [sg.Text("Job Title HTML Element"),sg.Text("(help)",key=GUI.PROFILEELEMENTS.CSSSELECTORHELP,enable_events=True,font=('default',7,'underline')),sg.Push()],
                     [sg.Text("Job Desc HTML Element"),sg.Text("(help)",key=GUI.PROFILEELEMENTS.CSSSELECTORHELP1,enable_events=True,font=('default',7,'underline')),sg.Push()]
                     ]),
             sg.Col([[sg.In(key=GUI.PROFILEELEMENTS.JOBKEYID, expand_x=True)],
                     [sg.In(key=GUI.PROFILEELEMENTS.PAGEKEYID, default_text='page', expand_x=True)],
                     [sg.In(key=GUI.PROFILEELEMENTS.HTMLTITLEKEY, default_text='type.class; e.g. div.main', expand_x=True)],
                     [sg.In(key=GUI.PROFILEELEMENTS.HTMLDESCKEY, default_text='type.class; e.g. div.main', expand_x=True)],
                     ])],
            ], expand_x=True, expand_y=True)
        config_layout = sg.Col([
            [header_panel_layout],
            # [search_spec_layout],
            ],expand_x=True, expand_y=True)
        
        link_peek_layout = sg.Col([
            [sg.Text("Job Identifying Keyword Help")],
            [sg.Listbox([], expand_x=True, expand_y=True, key=GUI.PROFILEELEMENTS.LINKS)],
            [sg.Button('Peek Links', key=GUI.PROFILEELEMENTS.PEEKLINKS)]
            ], expand_x=True, expand_y=True)
        desc_peek_layout = sg.Col([
            [sg.Text("Job Desc HTML Element Help")],
            [sg.Multiline('', expand_x=True, expand_y=True, key=GUI.PROFILEELEMENTS.DESCRIPTION)],
            [sg.Button('Peek Description', key=GUI.PROFILEELEMENTS.PEEKDESC)]
            ], expand_x=True, expand_y=True)
        peek_layout = sg.Col([
            [sg.Text("Config Assistance")],
            [link_peek_layout],
            [desc_peek_layout]
        ],expand_x=True, expand_y=True)

        method_layout = sg.Col([
            [sg.Text("Method Configuration")],
            [sg.Col([[sg.Text("Expected Reponses-")],
             [sg.Text("  of Search:"),
             sg.Radio("HTML", GUI.PROFILEELEMENTS.SEARCHRETTYPE, key = GUI.PROFILEELEMENTS.SEARCHRETTYPESHTML, default=True),
             sg.Radio("JSON", GUI.PROFILEELEMENTS.SEARCHRETTYPE, key = GUI.PROFILEELEMENTS.SEARCHRETTYPESJSON)],
             [sg.Text("  of Descriptions:"),
             sg.Radio("HTML", GUI.PROFILEELEMENTS.DESCRETTYPE, key = GUI.PROFILEELEMENTS.DESCRETTYPESHTML, default=True),
             sg.Radio("JSON", GUI.PROFILEELEMENTS.DESCRETTYPE, key = GUI.PROFILEELEMENTS.DESCRETTYPESJSON)]])],
            [sg.Col([[sg.Text("Render Required-")],
             [sg.Text("  of Search:"),
             sg.Radio("No", GUI.PROFILEELEMENTS.SEARCHRENREQ, key = GUI.PROFILEELEMENTS.SEARCHRENREQNO, default=True),
             sg.Radio("Yes", GUI.PROFILEELEMENTS.SEARCHRENREQ, key = GUI.PROFILEELEMENTS.SEARCHRENREQYES)],
             [sg.Text("  of Descriptions:"),
             sg.Radio("No", GUI.PROFILEELEMENTS.DESCRENREQ, key = GUI.PROFILEELEMENTS.DESCRENREQNO, default=True),
             sg.Radio("Yes", GUI.PROFILEELEMENTS.DESCRENREQ, key = GUI.PROFILEELEMENTS.DESCRENREQYES),]])],
             [search_spec_layout],
            # [sg.Listbox([], expand_x=True, expand_y=True, key=GUI.PROFILEELEMENTS.METHOD)],
            # [sg.Button('/\\', key=GUI.PROFILEELEMENTS.METHUP, font=('bitstream charter',8)), sg.Button('\\/', key=GUI.PROFILEELEMENTS.METHDOWN, font=('bitstream charter',8))],
        ],expand_x=True, expand_y=True)

        search_phrase_layout = sg.Col([
            [sg.Multiline(size=(25,8), key=GUI.PROFILEELEMENTS.SEARCHPHRASES),sg.Button('Commit Phrases', key=GUI.PROFILEELEMENTS.COMMITPHRASES)],
            ], expand_x=True, expand_y=True)

        #JOBS LAYOUT

        #TAB LAYOUT
        search_panel_layout = [
            [config_layout, method_layout,peek_layout],
            [sg.Button('Commit Changes', key=GUI.PROFILEELEMENTS.ADDSEARCH)],
            [search_phrase_layout]
            ]
        job_panel_layout = [
            [sg.Button('Find Current Jobs', key=GUI.PROFILEELEMENTS.GETCURRENTJOBS)],
            [sg.Multiline(size=(70,20),key=GUI.PROFILEELEMENTS.JOBSTATUSUPDATE)],
            [sg.Button('View Jobs', key=GUI.PROFILEELEMENTS.JOBSDETAIL)]
        ]
        tabs = sg.TabGroup([[
            sg.Tab('Config', search_panel_layout),
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
            GUI.PROFILEELEMENTS.CSSSELECTORHELP:partial(self.cssSelectorHelp, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PROFILEELEMENTS.CSSSELECTORHELP1:partial(self.cssSelectorHelp, window=w, profile=self.portfolio.profiles[profile]),
            }
        return w
    
    def cssSelectorHelp(self, values, window:sg.Window, profile:Profile):
        webbrowser.open('https://www.w3schools.com/cssref/css_selectors.php')

    def peekDesc(self, values, window:sg.Window, profile:Profile):
        if profile.name == GUI.NEWPROFILE:
            self.errorMsg("Must first commit search to create profile.")
        else:
            window[GUI.PROFILEELEMENTS.DESCRIPTION].update(value=profile.samplePosts())

    def openJobDetail(self, values, window:sg.Window, profile:Profile):
        self.jobsWindow(profile.name)

    def getCurrentJobs(self, values, window:sg.Window, profile:Profile, updateProfWin=True):
        self.portfolio.getNewJobsByProfile(profile)
        if updateProfWin:
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
        def getSlctn(w,e,v):
            s = None
            try:
                s = w[SRCH].Widget.selection_get()
            except tkinter.TclError:
                s = 'NOSEARCHKEYWORD-REPLACETHIS'
            return s
        modEv = {
            CNFBTTN:getSlctn
        }
        selection = self.__newWindow('Search Phrase',lyt,modal=True, modalEvents=modEv, modalCloseSet=set([CNFBTTN]))
        return selection
    
    def __getSearch(self, values, searchReq:Request)->Search:
        methConfig = self.__getMethodConfig(values=values)
        orgName = None
        if methConfig[GUI.PROFILEELEMENTS.PROFILENAME] != '':
            orgName = methConfig[GUI.PROFILEELEMENTS.PROFILENAME]
        search = Search.bySearchRequest(
            searchReq=searchReq,
            orgName=orgName,
            jobKeyId=methConfig[GUI.PROFILEELEMENTS.JOBKEYID],
            pageKeyId=methConfig[GUI.PROFILEELEMENTS.PAGEKEYID],
            titleKey=methConfig[GUI.PROFILEELEMENTS.HTMLTITLEKEY],
            descKey=methConfig[GUI.PROFILEELEMENTS.HTMLDESCKEY],
            jobListRetType=methConfig[GUI.PROFILEELEMENTS.SEARCHRETTYPE],
            jobDescRetType=methConfig[GUI.PROFILEELEMENTS.DESCRETTYPE],
            listRenReq=methConfig[GUI.PROFILEELEMENTS.SEARCHRENREQ],
            descRenReq=methConfig[GUI.PROFILEELEMENTS.DESCRENREQ],
            )
        return search
    
    def __getMethodConfig(self, values):
        retTypes = ['html','json']
        searchRetTypeSelection = [
            values[GUI.PROFILEELEMENTS.SEARCHRETTYPESHTML],
            values[GUI.PROFILEELEMENTS.SEARCHRETTYPESJSON],
        ].index(True)
        descRetTypeSelection = [
            values[GUI.PROFILEELEMENTS.DESCRETTYPESHTML],
            values[GUI.PROFILEELEMENTS.DESCRETTYPESJSON],
        ].index(True)
        renReqs = [False, True]
        searchRenReqSelection = [
            values[GUI.PROFILEELEMENTS.SEARCHRENREQNO],
            values[GUI.PROFILEELEMENTS.SEARCHRENREQYES],
        ].index(True)
        descRenReqSelection = [
            values[GUI.PROFILEELEMENTS.DESCRENREQNO],
            values[GUI.PROFILEELEMENTS.DESCRENREQYES],
        ].index(True)
        return {
            GUI.PROFILEELEMENTS.SEARCHRETTYPE: retTypes[searchRetTypeSelection],
            GUI.PROFILEELEMENTS.DESCRETTYPE: retTypes[descRetTypeSelection],
            GUI.PROFILEELEMENTS.SEARCHRENREQ: renReqs[searchRenReqSelection],
            GUI.PROFILEELEMENTS.DESCRENREQ: renReqs[descRenReqSelection],
            GUI.PROFILEELEMENTS.JOBKEYID:values[GUI.PROFILEELEMENTS.JOBKEYID],
            GUI.PROFILEELEMENTS.PAGEKEYID:values[GUI.PROFILEELEMENTS.PAGEKEYID],
            GUI.PROFILEELEMENTS.HTMLTITLEKEY:values[GUI.PROFILEELEMENTS.HTMLTITLEKEY],
            GUI.PROFILEELEMENTS.HTMLDESCKEY:values[GUI.PROFILEELEMENTS.HTMLDESCKEY],
            GUI.PROFILEELEMENTS.PROFILENAME:values[GUI.PROFILEELEMENTS.PROFILENAME],
        }
    
    def __getSearchRequest(self, values, window:sg.Window, srchPhrs)->Request:
        searchHeader = Transform().GUICurlToRequest(
            values[GUI.PROFILEELEMENTS.MLSEARCHHEADER],
            srchPhrs)
        return searchHeader

    def peekLinks(self, values, window:sg.Window):
        if values[GUI.PROFILEELEMENTS.MLSEARCHHEADER] == '':
            self.errorMsg("Must fill the search parameter 'Header'")
        else:
            fake_key = 'NEVERINAMILLIONYEARS'
            search_header = self.__getSearchRequest(values, window, fake_key)
            search = self.__getSearch(values, search_header)
            links = search.peekLinks(reqDict=search_header.getRequestDict(fake_key))
            window[GUI.PROFILEELEMENTS.LINKS].update(links)

    def addSearch(self, values, window:sg.Window, profile:Profile):
        if profile.name == GUI.NEWPROFILE and '' in {values[GUI.PROFILEELEMENTS.MLSEARCHHEADER],
                  values[GUI.PROFILEELEMENTS.JOBKEYID],
                  values[GUI.PROFILEELEMENTS.PAGEKEYID],
                  values[GUI.PROFILEELEMENTS.HTMLDESCKEY]}:
            self.errorMsg("Must fill the search parameters:\n\t\u2022'Header'\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        elif '' in {values[GUI.PROFILEELEMENTS.JOBKEYID],
                  values[GUI.PROFILEELEMENTS.PAGEKEYID],
                  values[GUI.PROFILEELEMENTS.HTMLDESCKEY]}:
            self.errorMsg("Must fill the search parameters:\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        else:
            if '' == values[GUI.PROFILEELEMENTS.MLSEARCHHEADER]:
                profile.search.setJobKeyId(values[GUI.PROFILEELEMENTS.JOBKEYID])
                profile.search.setPageKeyId(values[GUI.PROFILEELEMENTS.PAGEKEYID])
                profile.search.setTitleKey(values[GUI.PROFILEELEMENTS.HTMLTITLEKEY])
                profile.search.setDescKey(values[GUI.PROFILEELEMENTS.HTMLDESCKEY])
                if profile.getName() != values[GUI.PROFILEELEMENTS.PROFILENAME]:
                    window = self.__updatePortfolio(values, window, profile, renameProfile=True)
            else:
                srchPhrs = self.searchPhraseWindow(values[GUI.PROFILEELEMENTS.MLSEARCHHEADER])
                searchHeader = self.__getSearchRequest(values, window, srchPhrs)
                search = self.__getSearch(values=values, 
                                          searchReq=searchHeader)
                search.addSearchPhrase(Transform.HTMLTextToPlain(srchPhrs))
                if profile.name != GUI.NEWPROFILE:
                    profile.defineSearch(search)
                else:
                    profile = Profile.bySearch(search)
                    window = self.__updatePortfolio(values, window, profile)
            self.refreshSearchConfigVisual(window, profile)
    
    def __updatePortfolio(self, values, window:sg.Window, profile:Profile, renameProfile:bool=False):
        if renameProfile:
            self.portfolio.renameProfile(profile, values[GUI.PROFILEELEMENTS.PROFILENAME])
        else:
            self.portfolio.addProfile(profile)
        self.primaryWindow[GUI.MAINELEMENTS.PROFILES].update([k for k in self.portfolio.profiles.keys()])
        tmpwin = self.profileWindow(profile.name)
        self.__closeWindow(window)
        window = tmpwin
        return window

    def refreshSearchConfigVisual(self, window:sg.Window, profile:Profile):
        window[GUI.PROFILEELEMENTS.PROFILENAME].update(profile.getName())
        window[GUI.PROFILEELEMENTS.JOBKEYID].update(profile.search.getJobKeyId())
        window[GUI.PROFILEELEMENTS.PAGEKEYID].update(profile.search.getPageKeyId())
        window[GUI.PROFILEELEMENTS.HTMLTITLEKEY].update(profile.search.getTitleKey())
        window[GUI.PROFILEELEMENTS.HTMLDESCKEY].update(profile.search.getDescKey())
        window[GUI.PROFILEELEMENTS.SEARCHPHRASES].update('\n'.join(profile.search.getSearchPhrases()))
        window[[GUI.PROFILEELEMENTS.SEARCHRETTYPESHTML,
                GUI.PROFILEELEMENTS.SEARCHRETTYPESJSON][['html','json'].index(profile.search.getJobListRetType())]].update(True)
        window[[GUI.PROFILEELEMENTS.DESCRETTYPESHTML,
                GUI.PROFILEELEMENTS.DESCRETTYPESJSON][['html','json'].index(profile.search.getJobDescRetType())]].update(True)
        window[[GUI.PROFILEELEMENTS.SEARCHRENREQNO,
                GUI.PROFILEELEMENTS.SEARCHRENREQYES][profile.search.getListRenReq()]].update(True)
        window[[GUI.PROFILEELEMENTS.DESCRENREQNO,
                GUI.PROFILEELEMENTS.DESCRENREQYES][profile.search.getDescRenReq()]].update(True)

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
        FILTER = enum.auto()
        JOBLIST = enum.auto()
        JOBDESC = enum.auto()
        RESUME = enum.auto()
        CREATERESUME = enum.auto()
        # GETTIPS = enum.auto()
    class JOBLISTHEADINGS(enum.Enum):
        Job = enum.auto()
        Company = enum.auto()
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
        resume_access_layout = sg.Col([
            [sg.Text("Resume Management")],
            [sg.Combo(['','Test'], key=GUI.JOBELEMENTS.RESUME, expand_x=True)],
            [sg.Button('Create Resume', key=GUI.JOBELEMENTS.CREATERESUME)],
            ], expand_x=True, expand_y=True)
        
        # GPT_layout = sg.Col([
        #     [sg.Text("LLM Tips")],
        #     [sg.Multiline(key=GUI.JOBELEMENTS.RESUME, expand_x=True, expand_y=True)],
        #     [sg.Button('Get Tips', key=GUI.JOBELEMENTS.GETTIPS)],
        #     ], expand_x=True, expand_y=True)
        # resume_layout = sg.Col([
        #     [sg.Text("Resume Changes")],
        #     [sg.Multiline(expand_x=True, expand_y=True)],
        #     [sg.Button('Update Resume', key=GUI.JOBELEMENTS.UPDATERESUME)],
        #     ], expand_x=True, expand_y=True)
        
        layout_l = [[job_list_panel_layout]]
        layout_c = [[job_desc_layout]]
        layout_r = [[resume_access_layout]]

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
            GUI.JOBELEMENTS.CREATERESUME:partial(self.createResume, window=w),
            }
        return w
    
    def createResume(self, values, window:sg.Window):
        #TODO
        #Need to provide job selection and resume basis selection.
        #job selection -> where resume json, tex, and pdf will be saved
        #resume basis -> where resume json will be pulled from, providing available experience in opened resume window

        w = self.resumeWindow('test', r)


    def viewWebsite(self, values, window:sg.Window):
        jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
        dispJob = jobs[values[GUI.JOBELEMENTS.JOBLIST][0]][GUI.JOBLISTHEADINGS.Job.value-1]
        dispCompany = jobs[values[GUI.JOBELEMENTS.JOBLIST][0]][GUI.JOBLISTHEADINGS.Company.value-1]
        for v in values[GUI.JOBELEMENTS.JOBLIST]:
            webbrowser.open(self.portfolio.historicalPosts[dispCompany][dispJob].getLink())
    
    def displayJobDesc(self, values, window:sg.Window):
        if values[GUI.JOBELEMENTS.JOBLIST]:
            jobs = window[GUI.JOBELEMENTS.JOBLIST].get()
            dispJob = jobs[values[GUI.JOBELEMENTS.JOBLIST][0]][GUI.JOBLISTHEADINGS.Job.value-1]
            dispCompany = jobs[values[GUI.JOBELEMENTS.JOBLIST][0]][GUI.JOBLISTHEADINGS.Company.value-1]
            window[GUI.JOBELEMENTS.JOBDESC].update(value=self.portfolio.historicalPosts[dispCompany][dispJob].displayDescription())
    
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
            return values[GUI.JOBELEMENTS.FILTER] == '' or values[GUI.JOBELEMENTS.FILTER] in k[0]
        tableDict = filter(filt, self.portfolio.historicalPosts.items())
        currentSelection = set()
        if GUI.JOBELEMENTS.JOBLIST in values:
            currentSelection = window[GUI.JOBELEMENTS.JOBLIST].get()
            currentSelection = set(
                (currentSelection[x][GUI.JOBLISTHEADINGS.Job.value-1], currentSelection[x][GUI.JOBLISTHEADINGS.Company.value-1])
                for x in values[GUI.JOBELEMENTS.JOBLIST])
        newSelection = []
        table = []
        idxTrack = 0
        for i, (c_name, c_jobs) in enumerate(tableDict):
            for j, (p_name, p_job) in enumerate(c_jobs.items()):
                table.append([p_name, c_name, p_job.getStatus()])
                if (p_name, c_name) in currentSelection:
                    newSelection.append(idxTrack)
                idxTrack += 1
        window[GUI.JOBELEMENTS.JOBLIST].update(values=table, select_rows=newSelection)

    ####RESUME MODULE####
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
        BACK = enum.auto()
        NEXT = enum.auto()
    @staticmethod
    def RESUMEWINDOWLAYOUT(orgResume:Resume, revResume:ResumeRevision, page=1):
        revResume.resetMappings()

        class KeyCount:
            def __init__(self) -> None:
                self.counts = {k:0 for k in GUI.RESUMEELEMENTS}
            def getKey(self, k):
                ret = self.counts[k]
                self.counts[k] += 1
                return (k, ret)
        exp_col_sizes = [(70,3),(5,3),(70,3),(70,3)]
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
                    for e in ss.getElements():
                        rev_key_keep = keys.getKey(GUI.RESUMEELEMENTS.EXPKEEP)
                        rev_key_rev = keys.getKey(GUI.RESUMEELEMENTS.EXPREVISION)
                        revResume.addMapping(rev_key_keep, id(e))
                        revResume.addMapping(rev_key_rev, id(e))
                        l.append([sg.Multiline(e, key=keys.getKey(GUI.RESUMEELEMENTS.EXPERIENCE), size=exp_col_sizes[0]),
                                  sg.Checkbox('', default=revResume.getValueByID(id(e), "Keep"), key=rev_key_keep, size=exp_col_sizes[1]),
                                  sg.Multiline(revResume.getValueByID(id(e)), key=rev_key_rev, size=exp_col_sizes[2]),
                                  sg.Multiline("", key=keys.getKey(GUI.RESUMEELEMENTS.AIEXP), size=exp_col_sizes[3]),])
                        
                elif ss.getType() == Subsection.Types.SKILL:
                    l.append([sg.Text(ss.getSubject(), size=label_col_sizes[0]),
                              sg.Text("", size=label_col_sizes[1]),
                              sg.Text("", size=label_col_sizes[2]),
                              sg.Text("", size=label_col_sizes[3]),
                              ])
                    if isinstance(ss.getElements()[0], str):
                        l.append([sg.Multiline(','.join(ss.getElements()), key=keys.getKey(GUI.RESUMEELEMENTS.SKILL), size=exp_col_sizes[0]),
                                    sg.Checkbox('', default=True, key=keys.getKey(GUI.RESUMEELEMENTS.SKLKEEP), size=exp_col_sizes[1]),
                                    sg.Multiline(','.join(ss.getElements()), key=keys.getKey(GUI.RESUMEELEMENTS.SKLREVISION), size=exp_col_sizes[2]),
                                    sg.Multiline("", key=keys.getKey(GUI.RESUMEELEMENTS.AISKILL), size=exp_col_sizes[3]),])
                    else:
                        for sss in ss.getElements():
                            l.append([sg.Text('\t'+sss.getSubject(), size=label_col_sizes[0]),
                                    sg.Text("", size=label_col_sizes[1]),
                                    sg.Text("", size=label_col_sizes[2]),
                                    sg.Text("", size=label_col_sizes[3]),
                                    ])
                            l.append([sg.Multiline(','.join(sss.getElements()), key=keys.getKey(GUI.RESUMEELEMENTS.SKILL), size=exp_col_sizes[0]),
                                    sg.Checkbox('', default=True, key=keys.getKey(GUI.RESUMEELEMENTS.SKLKEEP), size=exp_col_sizes[1]),
                                    sg.Multiline(','.join(sss.getElements()), key=keys.getKey(GUI.RESUMEELEMENTS.SKLREVISION), size=exp_col_sizes[2]),
                                    sg.Multiline("", key=keys.getKey(GUI.RESUMEELEMENTS.AISKILL), size=exp_col_sizes[3]),])

        keys = KeyCount()
        org_resume_layout = []
        sec = orgResume.getSections()[page]
        addContent(org_resume_layout, sec.getContent())
        org_resume_layout += [[sg.Button("Back", key=GUI.RESUMEELEMENTS.BACK),sg.Button("Next", key=GUI.RESUMEELEMENTS.NEXT)]]
        org_resume_layout = sg.Frame(sec.getTitle(), org_resume_layout)

        org_resume_layout = sg.Col([
            [sg.Text("", size=label_col_sizes[0]),
             sg.Text("", size=label_col_sizes[1]),
             sg.Text("", size=label_col_sizes[2]),
             sg.Button("Get AI Tips",key=GUI.RESUMEELEMENTS.RUNAI, size=label_col_sizes[3])],
            [sg.Text("Resume", size=label_col_sizes[0], justification='center'),
             sg.Text("Keep", size=label_col_sizes[1], justification='center'),
             sg.Text("Revisions", size=label_col_sizes[2], justification='center'),
             sg.Text("Rating and Keywords", size=label_col_sizes[3], justification='center')],
             [org_resume_layout],
            ],
            expand_x=True,
            expand_y=True,
            # scrollable=True,
            # vertical_scroll_only=True,
            # justification='center',
            # element_justification='center',
            # size=(300, 200)
            )

        return [
            [org_resume_layout],
            [sg.Button('Update Resume', key=GUI.RESUMEELEMENTS.SAVEJSON),
            sg.Button('Generate PDF', key=GUI.RESUMEELEMENTS.SAVEPDF)]
        ]
        

    def resumeWindow(self, job, orgResume, revResume=None, page=0, loc=(None,None)):
        if revResume is None:
            revResume = ResumeRevision.fromResume(orgResume)
        w = self.__newWindow("Resume - {}".format(job),
                             GUI.RESUMEWINDOWLAYOUT(orgResume, revResume, page=page),
                             modal=True,
                             modalEvents={
                                 GUI.RESUMEELEMENTS.BACK:partial(
                                     self.pageResume,
                                     job=job,
                                     orgResume=orgResume,
                                     revResume=revResume,
                                     page=(page-1)%len(orgResume.getSections())),
                                 GUI.RESUMEELEMENTS.NEXT:partial(
                                     self.pageResume,
                                     job=job,
                                     orgResume=orgResume,
                                     revResume=revResume,page=(page+1)%len(orgResume.getSections())),
                                 },
                                 modalCloseSet=set([GUI.RESUMEELEMENTS.BACK,
                                                    GUI.RESUMEELEMENTS.NEXT]),
                             resizable=True,
                             loc=loc)
        return w
    
    def pageResume(self, window:sg.Window, event, values, job, orgResume, revResume:ResumeRevision, page):
        for k, v in values.items():
            if k[0] == GUI.RESUMEELEMENTS.EXPKEEP:
                revResume.markKeep(key=k, mark=v)
            if k[0] == GUI.RESUMEELEMENTS.EXPREVISION:
                revResume.setRevision(key=k, revision=v)
        loc = window.CurrentLocation()
        window.close()
        self.resumeWindow(job=job, orgResume=orgResume, revResume=revResume, page=page, loc=loc)
    
    def getTips(self, values, window:sg.Window):
        #TODO
        r = None
        with open('./Resumes/main/resume.pkl','rb') as f:
            r = pickle.load(f)
        tips = self.llm.getTips(r.asString(bulletsOnly=True, skipEdu=True, lineNums=True), values[GUI.JOBELEMENTS.JOBDESC])
        window[GUI.RESUMEELEMENTS.RESUME].update(tips)

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

def main(LLM_API_Key=''):
    port:Portfolio = Portfolio()
    port.addProfile(Profile(GUI.NEWPROFILE))
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            port = pickle.load(f)
    llm = None
    if LLM_API_Key:
        llm = LLM(LLM_API_Key)
    gui = GUI(portfolio=port, llm=llm)

    gui.mainWindow()

    gui.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--LLM_API_Key')
    args = parser.parse_args()
    main(LLM_API_Key=args.LLM_API_Key)