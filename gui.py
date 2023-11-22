import PySimpleGUI as sg

from Search.transforms import Transform
from Search.profile import (
    Profile,
    Portfolio
)
from Search.search import Search
from Search.utility import request

import pickle
from pathlib import Path
from typing import (
    Dict
)
from functools import partial

class GUI:
    def __init__(self, portfolio:Portfolio) -> None:
        self.windows:Dict[str, sg.Window] = {}
        self.primaryWindow:sg.Window = None
        self.portfolio:Portfolio = portfolio

    def __newWindow(self, name, layout, modal=False, enable_close_attempted_event=False, resizable=False, modalEvents={}, modalCloseSet=set('OK')):
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
    JOBSDETAIL = 'Detail'
    ALLNEWJOBS = 'Get All New Jobs'
    OPENPROFILE = "Access Profile"
    @staticmethod
    def MAINWINDOWLAYOUT(profiles):
        profile_panel_layout = sg.Col([
            [sg.Text("Profiles")],
            [sg.Listbox([k for k in profiles.keys()], expand_x=True, expand_y=True, key="PROFILES")],
            [sg.Button(GUI.OPENPROFILE)]
            ], expand_x=True, expand_y=True)
        jobs_panel_layout = sg.Col([
            [sg.Text("Jobs")],
            [sg.vtop(sg.Button(GUI.JOBSDETAIL)), sg.Col([[sg.Button(GUI.ALLNEWJOBS)],
                    [sg.Multiline(size=(100,50), key="NEWJOBS")]], pad=((0,0),(0,1)))],
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
        self.primaryWindow = w
        self.windows[w] = {
            GUI.OPENPROFILE:self.openProfile,
            sg.WIN_X_EVENT:self.endProgram,
            GUI.JOBSDETAIL:..., #TODO
            GUI.ALLNEWJOBS:... #TODO
            }
    
    def openProfile(self, values):
        for p in values['PROFILES']:
            self.profileWindow(p)
    
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

    PEEKLINKS = "Peek Links"
    ADDSEARCH = "Commit Search"
    COMMITPHRASES = "Commit Phrases"
    MLSEARCHHEADER = "SEARCH"
    LINKS = "LINKS"
    KEYID = "KEYID"
    HTMLKEY = "HTMLKEY"
    SEARCHPHRASES = "SEARCHPHRASES"
    @staticmethod
    def PROFILESWINDOWLAYOUT():
        header_panel_layout = sg.Col([
            [sg.Text("Sample Header")],
            [sg.Multiline(key=GUI.MLSEARCHHEADER, size=(100,20), expand_x=True, expand_y=True)],
            ], expand_x=True, expand_y=True)
        link_peak_layout = sg.Col([
            [sg.Text("Job Identifying Keyword Help")],
            [sg.Listbox([], expand_x=True, expand_y=True, key=GUI.LINKS)],
            [sg.Button(GUI.PEEKLINKS)]
            ], expand_x=True, expand_y=True)
        search_spec_layout = sg.Col([
            [sg.Col([[sg.Text("Link Keyword Identifying Jobs")],
                     [sg.Text("Job Desc HTML element")]]),
             sg.Col([[sg.In(key=GUI.KEYID, expand_x=True)],
                     [sg.In(key=GUI.HTMLKEY, default_text='type.class; e.g. article.node--type-job-opportunity', expand_x=True)],
                     ])],
            ], expand_x=True, expand_y=True)
        search_phrase_layout = sg.Col([
            [sg.Multiline(size=(25,8), key=GUI.SEARCHPHRASES),sg.Button(GUI.COMMITPHRASES)],
            ], expand_x=True, expand_y=True)
        search_panel_layout = sg.Col([
            [sg.Text("Search Parameters")],
            [header_panel_layout, link_peak_layout],
            [search_spec_layout],
            [sg.Button(GUI.ADDSEARCH)],
            [search_phrase_layout]
            ], expand_x=True, expand_y=True)
        

        layout_l = [[search_panel_layout]]
        layout_c = [[]]
        layout_r = [[]]

        return [
            [
                sg.Col(layout_l, expand_x=True, expand_y=True),
            ]
        ]
            
    def profileWindow(self, profile:str):
        w = self.__newWindow(profile, GUI.PROFILESWINDOWLAYOUT(), resizable=True)
        self.windows[w] = {
            GUI.ADDSEARCH:partial(self.addSearch, window=w, profile=self.portfolio.profiles[profile]),
            GUI.PEEKLINKS:partial(self.peekLinks, window=w),
            GUI.COMMITPHRASES:partial(self.commitPhrases, window=w, profile=self.portfolio.profiles[profile])
            }
        return w
    
    def commitPhrases(self, values, window:sg.Window, profile:Profile):
        srchPhrss = values[GUI.SEARCHPHRASES].split('\n')
        profile.search.setSearchPhrases(srchPhrss)
        window[GUI.SEARCHPHRASES].update('\n'.join(profile.search.searchPhrases))

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
        if values[GUI.MLSEARCHHEADER] == '':
            self.errorMsg("Must fill the search parameter 'Header'")
        else:
            search_header = Transform().GUIRequestHeaderToRequestParamDict(values[GUI.MLSEARCHHEADER])
            search = request(searchReq=search_header)
            window[GUI.LINKS].update([l for l in search.html.links])

    def addSearch(self, values, window:sg.Window, profile:Profile):
        if '' in {values[GUI.MLSEARCHHEADER], values[GUI.KEYID], values[GUI.HTMLKEY]}:
            self.errorMsg("Must fill the search parameters, 'Header' and 'Job Indetifying Keyword'")
        else:
            search_header = Transform().GUIRequestHeaderToRequestParamDict(values[GUI.MLSEARCHHEADER])
            srchPhrs = self.searchPhraseWindow(values[GUI.MLSEARCHHEADER])
            search_header['url'] = search_header['url'].replace(srchPhrs, '{}')
            search = Search.byHTML(searchReq=search_header, jobKeyId=values[GUI.KEYID], descKey=values[GUI.HTMLKEY])
            search.addSearchPhrase(Transform.HTMLTextToPlain(srchPhrs))
            if profile.name != GUI.NEWPROFILE:
                profile.defineSearch(search)
            else:
                profile = Profile.bySearch(search)
                self.portfolio.addProfile(profile)
                self.primaryWindow['PROFILES'].update([k for k in self.portfolio.profiles.keys()])
                tmpwin = self.profileWindow(profile.name)
                self.__closeWindow(window)
                window = tmpwin
            self.refreshSearchConfigVisual(window, profile)
    
    def refreshSearchConfigVisual(self, window:sg.Window, profile:Profile):
        window[GUI.KEYID].update(profile.search.jobKeyId)
        window[GUI.HTMLKEY].update(profile.search.descKey)
        window[GUI.SEARCHPHRASES].update('\n'.join(profile.search.searchPhrases))

    def errorMsg(self, message):
        lyt = [
            [sg.Text(message)],
            [sg.Button("OK")]
            ]
        self.__newWindow("Error", lyt, modal=True)
    
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


def profileWindow(window, profileStr:str, profile:Profile):
    w = sg.Window(profileStr, PROFILESWINDOWLAYOUT(), location=window.current_location())

def JOBSWINDOWLAYOUT():
    pass


def main():
    port:Portfolio = Portfolio()
    port.addProfile(Profile(GUI.NEWPROFILE))
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            port = pickle.load(f)
    gui = GUI(portfolio=port)

    gui.mainWindow()

    gui.run()

if __name__ == "__main__":
    main()