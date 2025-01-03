import dearpygui.dearpygui as dpg
import webbrowser
from jobsearch.backend.backend import Backend
from jobsearch.search.transforms import Transform, Request
from jobsearch.search.profile import (
    Profile,
    Portfolio,
    Posting
)
from jobsearch.search.search import Search
from jobsearch.resumes.resume import Resume, Section, Subsection, ResumeRevision
from jobsearch.resumes.llm import LLM
from jobsearch.resumes.pdf import pdf
from jobsearch.search.utility import errorWindow, textWrapper
from jobsearch.gui.menu import Menu
from jobsearch.gui.module import Module
from typing import (
    List,
    Dict,
    Type,
    Union
)
import abc
import enum
import pickle
import traceback
from copy import deepcopy
import datetime


class GUISignIn(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        SELECTION = enum.auto()
        ADDUSER = enum.auto()

    def __init__(self, backend: Backend, primary_window: "GUIMain") -> None:
        super().__init__(backend)
        self.primary_window = primary_window

    def newWindow(self):
        tag = self.getKey(GUISignIn.ELEMENTS.WINDOW)
        with dpg.window(
            label="User Sign In",
            on_close=self.cleanAliases,
            tag=tag,
            autosize=True,
            pos=[300,300]
            ):
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_listbox(
                        self.backend.get_users(),
                        tag=self.getKey(GUISignIn.ELEMENTS.SELECTION),
                        num_items=8,
                        width=300)
                    dpg.add_button(label="Add", callback=self.add_user)
                dpg.add_button(label="Sign In", callback=self.sign_in)

    def sign_in(self):
        name = dpg.get_value(self.getKey(GUISignIn.ELEMENTS.SELECTION))
        self.backend.set_user(name)
        dpg.delete_item(self.getKey(GUISignIn.ELEMENTS.WINDOW))
        self.primary_window.newWindow()

    def add_user(self):
        au = GUIAddUser(backend=self.backend, menu=self)
        au.newWindow()

    def refresh_user_list(self):
        dpg.configure_item(
            self.getKey(GUISignIn.ELEMENTS.SELECTION),
            items=self.backend.get_users())
            
class GUIAddUser(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        NAME = enum.auto()
        ADDUSER = enum.auto()

    def __init__(self, backend: Backend, menu:GUISignIn) -> None:
        super().__init__(backend)
        self.menu = menu

    def newWindow(self):
        tag = self.getKey(GUIAddUser.ELEMENTS.WINDOW)
        with dpg.window(
            label="Create User",
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            tag=tag,
            width=300,
            modal=True
            ):
            dpg.add_input_text(
                label="User Name",
                tag=self.getKey(GUIAddUser.ELEMENTS.NAME))
            with dpg.group(horizontal=True):
                dpg.add_button(label="OK", callback=self.ok)
                dpg.add_button(label="Cancel", callback=self.cancel)

    def ok(self):
        name = dpg.get_value(self.getKey(GUIAddUser.ELEMENTS.NAME))
        self.backend.create_user(name)
        self.menu.refresh_user_list()
        dpg.delete_item(self.getKey(GUIAddUser.ELEMENTS.WINDOW))
    
    def cancel(self):
        dpg.delete_item(self.getKey(GUIAddUser.ELEMENTS.WINDOW))


class GUIMain(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        PROFILES = enum.auto()
        JOBSDETAIL = enum.auto()
        ALLNEWJOBS = enum.auto()
        NEWJOBS = enum.auto()
        OPENPROFILE = enum.auto()
    
    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)
        self.menu = Menu(backend=self.backend)

    def newWindow(self):
        tag = self.getKey(GUIMain.ELEMENTS.WINDOW)
        with dpg.window(tag=tag, on_close=self.cleanAliases):
            self.menu.newWindow()
            with dpg.group(horizontal=True):
                with dpg.group(width=500):
                    dpg.add_text("Profiles")
                    dpg.add_listbox(
                        [k for k in self.backend.get_profile_names()],
                        tag=self.getKey(GUIMain.ELEMENTS.PROFILES),
                        num_items=30)
                    dpg.add_button(
                        label="Access Profile",
                        tag=self.getKey(GUIMain.ELEMENTS.OPENPROFILE),
                        callback=self.openProfile)
                with dpg.group():
                    dpg.add_text("Jobs")
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Get All New Jobs",
                            tag=self.getKey(GUIMain.ELEMENTS.ALLNEWJOBS),
                            callback=self.getAllNewJobs)
                        dpg.add_button(
                            label="Detail",
                            tag=self.getKey(GUIMain.ELEMENTS.JOBSDETAIL),
                            callback=self.openJobs)
                    with dpg.child_window(width=500, height=500):
                        dpg.add_text("", wrap=800, tag=self.getKey(GUIMain.ELEMENTS.NEWJOBS))
        dpg.set_primary_window(tag, True)

    def openProfile(self, sender, app_data, user_data):
        profile_name = dpg.get_value(self.getKey(GUIMain.ELEMENTS.PROFILES))
        prof_mod = GUIProfile.fromProfileAndBackend(
            self.backend.select_profile_by_name(profile_name),
            backend=self.backend)
        prof_mod.newWindow()

    def openJobs(self, sender, app_data, user_data):
        job_mod = GUIJobs(self.backend)
        job_mod.newWindow()

    def getAllNewJobs(self, sender, app_data, user_data):
        windowUpdate = ''
        numNewJobs = 0 
        for p in self.backend.get_profiles():
            p.gatherPosts()
            numNewJobs += len(p.getCurrentPosts())
            windowUpdate += '\n{}:\n\t'.format(p.getName())
            windowUpdate += '\n\t'.join(p.getCurrentPosts().keys())
        dpg.set_value(self.getKey(GUIMain.ELEMENTS.NEWJOBS),'{} new jobs found:{}'.format(numNewJobs, windowUpdate))

class GUIProfile(Module):
    class OPTIONS:
        RETTYPE = ["html", "json"]
        RENREQ = ["No", "Yes"]
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        #Config Elements
        PEEKLINKS = enum.auto()
        ADDSEARCH = enum.auto()
        COMMITPHRASES = enum.auto()
        MLSEARCHHEADER = enum.auto()
        SEARCHRETTYPE = enum.auto()
        # SEARCHRETTYPESHTML = enum.auto()
        # SEARCHRETTYPESJSON = enum.auto()
        DESCRETTYPE = enum.auto()
        # DESCRETTYPESHTML = enum.auto()
        # DESCRETTYPESJSON = enum.auto()
        SEARCHRENREQ = enum.auto()
        # SEARCHRENREQNO = enum.auto()
        # SEARCHRENREQYES = enum.auto()
        DESCRENREQ = enum.auto()
        # DESCRENREQNO = enum.auto()
        # DESCRENREQYES = enum.auto()
        LINKSLL = enum.auto()
        LINKSTN = enum.auto()
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
        PROFILENAME = enum.auto()

        #Job Elements
        JOBSTATUSUPDATE = enum.auto()
        GETCURRENTJOBS = enum.auto()
        JOBSDETAIL = enum.auto()
    def __init__(
            self,
            profile,
            backend) -> None:
        super().__init__(backend=backend)
        self.profile:Profile = profile
    
    @classmethod
    def fromProfileAndBackend(cls, profile:Profile, backend:Backend):
        return cls(profile=profile, backend=backend)
    
    def getKey(self, k, withCount=False):
        k = self.profile.getName()+str(k)
        return super().getKey(k, withCount)
    
    def cleanAliases(self):
        super().cleanAliases()
        self.backend.quicksave_portfolio()
    
    def newWindow(self):
        column_widths = [200,200,-1]
        with dpg.window(
            label=self.profile.getName().upper(),
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            tag=self.getKey(GUIProfile.ELEMENTS.WINDOW),
            width=1400):
            with dpg.tab_bar():
                with dpg.tab(label="Config"):
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            with dpg.group(width=column_widths[0]):
                                with dpg.group(horizontal=True):
                                    dpg.add_text("Profile Name:")
                                    dpg.add_input_text(default_value=self.profile.getName(), tag=self.getKey(GUIProfile.ELEMENTS.PROFILENAME))
                                dpg.add_text("Sample Request")
                                dpg.add_input_text(multiline=True, tag=self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER))
                            with dpg.group(width=column_widths[1]):
                                dpg.add_text("Method Configuration")
                                dpg.add_text("Expected Reponses-")
                                with dpg.group(horizontal=True):
                                    dpg.add_text("  of Search:")
                                    dpg.add_radio_button(
                                        GUIProfile.OPTIONS.RETTYPE,
                                        horizontal=True,
                                        tag=self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE),
                                        default_value=self.profile.getSearch().getJobListRetType(),
                                        user_data={i:j for i,j in zip(GUIProfile.OPTIONS.RETTYPE, [GUIProfile.ELEMENTS.LINKSLL, GUIProfile.ELEMENTS.LINKSTN])},
                                        callback=self.peekLinkStructToggle)
                                with dpg.group(horizontal=True):
                                    dpg.add_text("  of Descriptions:")
                                    dpg.add_radio_button(
                                        GUIProfile.OPTIONS.RETTYPE,
                                        horizontal=True,
                                        tag=self.getKey(GUIProfile.ELEMENTS.DESCRETTYPE),
                                        default_value=self.profile.getSearch().getJobDescRetType())
                                dpg.add_text("Render Required-")
                                with dpg.group(horizontal=True):
                                    dpg.add_text("  of Search:")
                                    dpg.add_radio_button(
                                        GUIProfile.OPTIONS.RENREQ,
                                        horizontal=True,
                                        tag=self.getKey(GUIProfile.ELEMENTS.SEARCHRENREQ),
                                        default_value=GUIProfile.OPTIONS.RENREQ[self.profile.getSearch().getListRenReq()])
                                with dpg.group(horizontal=True):
                                    dpg.add_text("  of Descriptions:")
                                    dpg.add_radio_button(
                                        GUIProfile.OPTIONS.RENREQ,
                                        horizontal=True,
                                        tag=self.getKey(GUIProfile.ELEMENTS.DESCRENREQ),
                                        default_value=GUIProfile.OPTIONS.RENREQ[self.profile.getSearch().getDescRenReq()])
                                with dpg.group(horizontal=True):
                                    with dpg.group():
                                        dpg.add_text("Link Keyword Identifying Jobs")
                                        dpg.add_text("Link Keyword Identifying Pages")
                                        with dpg.group(horizontal=True):
                                            dpg.add_text("Job Title HTML Element")
                                            dpg.add_button(
                                                label="(help)",
                                                callback=self.cssSelectorHelp,
                                                small=True)
                                        with dpg.group(horizontal=True):
                                            dpg.add_text("Job Desc HTML Element")
                                            dpg.add_button(
                                                label="(help)",
                                                callback=self.cssSelectorHelp,
                                                small=True)
                                    with dpg.group():
                                        dpg.add_input_text(
                                            default_value=self.profile.getSearch().getJobKeyId(),
                                            tag=self.getKey(GUIProfile.ELEMENTS.JOBKEYID))
                                        dpg.add_input_text(
                                            default_value=self.profile.getSearch().getPageKeyId(),
                                            tag=self.getKey(GUIProfile.ELEMENTS.PAGEKEYID))
                                        dpg.add_input_text(
                                            default_value=self.profile.getSearch().getTitleKey(),
                                            tag=self.getKey(GUIProfile.ELEMENTS.HTMLTITLEKEY))
                                        dpg.add_input_text(
                                            default_value=self.profile.getSearch().getDescKey(),
                                            tag=self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY))
                            with dpg.group(width=column_widths[2]):
                                dpg.add_text("Config Assistance")
                                dpg.add_text("Job Identifying Keyword Help")
                                dpg.add_listbox(
                                    tag=self.getKey(GUIProfile.ELEMENTS.LINKSLL),
                                    num_items=10,
                                    show=dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE))==GUIProfile.OPTIONS.RETTYPE[0])
                                dpg.add_child_window(
                                    height=180,
                                    show=dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE))==GUIProfile.OPTIONS.RETTYPE[1],
                                    tag=self.getKey(GUIProfile.ELEMENTS.LINKSTN))
                                dpg.add_button(
                                    label="Peek Links",
                                    tag=self.getKey(GUIProfile.ELEMENTS.PEEKLINKS),
                                    callback=self.peekLinks)
                                dpg.add_text("Job Desc HTML Element Help")
                                dpg.add_input_text(
                                    tag=self.getKey(GUIProfile.ELEMENTS.DESCRIPTION),
                                    multiline=True,
                                    readonly=True,
                                    height=300)
                                dpg.add_button(
                                    label="Peek Description",
                                    tag=self.getKey(GUIProfile.ELEMENTS.PEEKDESC),
                                    callback=self.peekDesc)
                        with dpg.group():
                            dpg.add_button(
                                label="Commit Changes",
                                tag=self.getKey(GUIProfile.ELEMENTS.ADDSEARCH),
                                callback=self.addSearch)
                            with dpg.group(horizontal=True):
                                dpg.add_input_text(
                                    tag=self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES),
                                    width=150, height=60,
                                    multiline=True,
                                    default_value=self.profile.getSearch().getSearchPhrases(asString=True))
                                dpg.add_button(
                                    label="Commit Phrases",
                                    tag=self.getKey(GUIProfile.ELEMENTS.COMMITPHRASES),
                                    callback=self.commitPhrases)
                with dpg.tab(label="Jobs"):
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Find Current Jobs",
                            tag=self.getKey(GUIProfile.ELEMENTS.GETCURRENTJOBS),
                            callback=self.getCurrentJobs)
                        dpg.add_button(
                            label="View Jobs",
                            tag=self.getKey(GUIProfile.ELEMENTS.JOBSDETAIL),
                            callback=self.openJobDetail)
                    with dpg.child_window(width=600, height=400):
                        dpg.add_text("", wrap=600, tag=self.getKey(GUIProfile.ELEMENTS.JOBSTATUSUPDATE))

    def peekLinkStructToggle(self, sender, app_data, user_data):
        show = dpg.get_value(sender)
        for k, v in user_data.items():
            if k == show:
                dpg.configure_item(self.getKey(v), show=True)
            else:
                dpg.configure_item(self.getKey(v), show=False)

    def cssSelectorHelp(self, sender, app_data, user_data):
        webbrowser.open('https://www.w3schools.com/cssref/css_selectors.php')

    def peekDesc(self, sender, app_data, user_data):
        if self.profile.getName() == Profile.NEWPROFILE:
            errorWindow("Must first commit search to create profile.")
        else:
            dpg.set_value(self.getKey(GUIProfile.ELEMENTS.DESCRIPTION), self.profile.samplePosts())

    def openJobDetail(self, sender, app_data, user_data):
        job_mod = GUIJobs(backend=self.backend)
        job_mod.newWindow(self.profile.getName())

    def getCurrentJobs(self, sender, app_data, user_data):
        self.profile.gatherPosts()
        dpg.set_value(
            self.getKey(GUIProfile.ELEMENTS.JOBSTATUSUPDATE),
            '{} new jobs found:\n{}'.format(
                len(self.profile.getCurrentPosts()),
                '\n'.join(self.profile.getCurrentPosts().keys())))

    def commitPhrases(self, sender, app_data, user_data):
        srchPhrss = dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES)).split('\n')
        self.profile.getSearch().setSearchPhrases(srchPhrss)
        dpg.set_value(
            self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES),
            '\n'.join(self.profile.getSearch().getSearchPhrases()))

    def searchPhraseWindow(self, close_win):
        def getSlctn(sender, app_data, user_data):
            srchPhrs = dpg.get_value("temp")
            searchHeader = self.__getSearchRequest(srchPhrs)
            search = self.__getSearch(searchReq=searchHeader)
            search.addSearchPhrase(Transform.HTMLTextToPlain(srchPhrs))
            if self.profile.getName() != Profile.NEWPROFILE:
                self.profile.defineSearch(search)
            else:
                profile = Profile.bySearch(search)
                self.__updatePortfolio(profile)
            dpg.delete_item(user_data)
            if dpg.get_item_label(close_win) == Profile.NEWPROFILE.upper():
                dpg.delete_item(close_win)
        wrapped_text = textWrapper(
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)),
            wrap_len=65)
        def justClose(sender, app_data, user_data):
            dpg.delete_item(user_data)


        with dpg.window(label="Search Phrase", modal=True, height=600, width=500, tag="temp_win", user_data="temp_win", on_close=justClose):
            dpg.add_text("Please identify the\nsearch phrase in the url:")
            dpg.add_input_text(
                default_value=wrapped_text,
                width=-1, height=480,
                multiline=True,
                readonly=True)
            dpg.add_input_text(default_value="", width=300, tag="temp")
            dpg.add_button(label="Confirm", callback=getSlctn, user_data='temp_win')
    
    def __getSearch(self, searchReq:Request)->Search:
        methConfig = self.__getMethodConfig()
        orgName = None
        if methConfig[GUIProfile.ELEMENTS.PROFILENAME] != Profile.NEWPROFILE:
            orgName = methConfig[GUIProfile.ELEMENTS.PROFILENAME]
        search = Search.bySearchRequest(
            searchReq=searchReq,
            orgName=orgName,
            jobKeyId=methConfig[GUIProfile.ELEMENTS.JOBKEYID],
            pageKeyId=methConfig[GUIProfile.ELEMENTS.PAGEKEYID],
            titleKey=methConfig[GUIProfile.ELEMENTS.HTMLTITLEKEY],
            descKey=methConfig[GUIProfile.ELEMENTS.HTMLDESCKEY],
            jobListRetType=methConfig[GUIProfile.ELEMENTS.SEARCHRETTYPE],
            jobDescRetType=methConfig[GUIProfile.ELEMENTS.DESCRETTYPE],
            listRenReq=methConfig[GUIProfile.ELEMENTS.SEARCHRENREQ],
            descRenReq=methConfig[GUIProfile.ELEMENTS.DESCRENREQ],
            )
        return search
    
    def __getMethodConfig(self):
        return {
            GUIProfile.ELEMENTS.SEARCHRETTYPE: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE)),
            GUIProfile.ELEMENTS.DESCRETTYPE: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.DESCRETTYPE)),
            GUIProfile.ELEMENTS.SEARCHRENREQ: bool(GUIProfile.OPTIONS.RENREQ.index(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRENREQ)))),
            GUIProfile.ELEMENTS.DESCRENREQ: bool(GUIProfile.OPTIONS.RENREQ.index(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.DESCRENREQ)))),
            GUIProfile.ELEMENTS.JOBKEYID: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.JOBKEYID)),
            GUIProfile.ELEMENTS.PAGEKEYID: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PAGEKEYID)),
            GUIProfile.ELEMENTS.HTMLTITLEKEY: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLTITLEKEY)),
            GUIProfile.ELEMENTS.HTMLDESCKEY: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY)),
            GUIProfile.ELEMENTS.PROFILENAME: dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PROFILENAME)),
        }
    
    def __getSearchRequest(self, srchPhrs)->Request:
        searchHeader = Transform().GUICurlToRequest(
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)),
            srchPhrs)
        return searchHeader

    def peekLinks(self, sender, app_data, user_data):
        if dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)) == '':
            errorWindow("Must fill the search parameter 'Header'")
        else:
            fake_key = 'NEVERINAMILLIONYEARS'
            search_header = self.__getSearchRequest(fake_key)
            search = self.__getSearch(search_header)
            links = search.peekLinks(reqDict=search_header.getRequestDict(fake_key))
            if dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE))==GUIProfile.OPTIONS.RETTYPE[0]:
                dpg.configure_item(self.getKey(GUIProfile.ELEMENTS.LINKSLL), items=links)
            else:
                def build_tree(parent, json):
                    if isinstance(json, dict):
                        for k, itm in json.items():
                            p = dpg.add_tree_node(parent=parent, label=k)
                            build_tree(p, itm)
                    elif isinstance(json, list):
                        for i, itm in enumerate(json):
                            p = dpg.add_tree_node(parent=parent, label=i)
                            build_tree(p, itm)
                    else:
                        dpg.add_text(str(json), parent=parent)
                build_tree(self.getKey(GUIProfile.ELEMENTS.LINKSTN), links)

    def addSearch(self, sender, app_data, user_data):
        if self.profile.getName() == Profile.NEWPROFILE and '' in {
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)),
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.JOBKEYID)),
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PAGEKEYID)),
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY))}:
            errorWindow("Must fill the search parameters:\n\t\u2022'Header'\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        elif '' in {dpg.get_value(self.getKey(GUIProfile.ELEMENTS.JOBKEYID)),
                  dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PAGEKEYID)),
                  dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY))}:
            errorWindow("Must fill the search parameters:\n\t\u2022'Job Indetifying Keyword'\n\t\u2022'Page Indetifying Keyword'\n\t\u2022Description HTML Element")
        else:
            if '' == dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)):
                self.setSearchConfig()
                if self.profile.getName() != dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PROFILENAME)):
                    self.__updatePortfolio(self.profile, renameProfile=True)
                else:
                    self.refreshSearchConfigVisual(self.profile)
            else:
                win = dpg.get_active_window()
                self.searchPhraseWindow(win)
    
    def __updatePortfolio(self, profile:Profile, renameProfile:bool=False):
        window_to_close = self.getKey(GUIProfile.ELEMENTS.WINDOW)
        if renameProfile:
            self.backend.rename_profile(
                profile,
                dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PROFILENAME)))
        else:
            self.backend.add_profile(profile)
        dpg.configure_item(GUIMain().getKey(GUIMain.ELEMENTS.PROFILES), items=[k for k in self.backend.get_profile_names()])
        new_prof = GUIProfile.fromProfileAndBackend(profile=profile, backend=self.backend)
        new_prof.newWindow()
        self.cleanAliases()
        dpg.delete_item(window_to_close)

    def refreshSearchConfigVisual(self, profile:Profile):
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.PROFILENAME), profile.getName())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.JOBKEYID), profile.getSearch().getJobKeyId())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.PAGEKEYID), profile.getSearch().getPageKeyId())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.HTMLTITLEKEY), profile.getSearch().getTitleKey())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY), profile.getSearch().getDescKey())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES), '\n'.join(profile.getSearch().getSearchPhrases()))
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE), profile.getSearch().getJobListRetType())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.DESCRETTYPE), profile.getSearch().getJobDescRetType())
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRENREQ), GUIProfile.OPTIONS.RENREQ[profile.getSearch().getListRenReq()])
        dpg.set_value(self.getKey(GUIProfile.ELEMENTS.DESCRENREQ), GUIProfile.OPTIONS.RENREQ[profile.getSearch().getDescRenReq()])

    def setSearchConfig(self):
        self.profile.getSearch().setJobListRetType(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE)))
        self.profile.getSearch().setJobDescRetType(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.DESCRETTYPE)))
        self.profile.getSearch().setJobKeyId(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.JOBKEYID)))
        self.profile.getSearch().setPageKeyId(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PAGEKEYID)))
        self.profile.getSearch().setTitleKey(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLTITLEKEY)))
        self.profile.getSearch().setDescKey(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY)))
        self.profile.getSearch().setSearchPhrases(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES)).split('\n'))
        self.profile.getSearch().setListRenReq(bool(GUIProfile.OPTIONS.RENREQ.index(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.SEARCHRENREQ)))))
        self.profile.getSearch().setDescRenReq(bool(GUIProfile.OPTIONS.RENREQ.index(dpg.get_value(self.getKey(GUIProfile.ELEMENTS.DESCRENREQ)))))

class GUIJobs(Module):
    class ELEMENTS(enum.Enum):
        VIEWSITE = enum.auto()
        APPLIED = enum.auto()
        IGNORE = enum.auto()
        COMPFILTER = enum.auto()
        STATFILTER = enum.auto()
        JOBLIST = enum.auto()
        JOBDESC = enum.auto()
        RESUME = enum.auto()
        CREATERESUME = enum.auto()
        COMPROW = enum.auto()
        # GETTIPS = enum.auto()
    class HEADINGS(enum.Enum):
        Job = enum.auto()
        Company = enum.auto()
        Status = enum.auto()
        PullDate = enum.auto()
        RecentApp = enum.auto()

    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)
        self.table_selections = set([])
        self.table_company_rows = {}
        self.table_last_selected = None
        self.recent_time_unit = datetime.timedelta(6*30)
        
    def __filt_key(self, x:str,y:str):
        x = x.replace(',','').replace('-','')
        y = y.replace(',','').replace('-','')
        return "{}&{}".format(x, y)
    
    def __filt(self, s,a,u):
        comp_filt = dpg.get_value(self.getKey(GUIJobs.ELEMENTS.COMPFILTER))
        stat_filt = dpg.get_value(self.getKey(GUIJobs.ELEMENTS.STATFILTER))
        dpg.set_value(u, self.__filt_key(comp_filt, stat_filt))

    def __clear_table_selections(self, s, a, u):
        for s in self.table_selections:
            dpg.set_value(s, False)
        self.table_selections = set([])

    def __select_call(self, s, a, u):
        if dpg.is_key_down(dpg.mvKey_LShift) or dpg.is_key_down(dpg.mvKey_RShift):
            row = dpg.get_item_parent(s)
            table = dpg.get_item_parent(row)
            rows = dpg.get_item_children(table)[1]
            start_idx = rows.index(dpg.get_item_parent(self.table_last_selected))+1
            end_idx = rows.index(row)
            if end_idx < start_idx:
                temp = end_idx
                end_idx = start_idx
                start_idx = temp
            for r in rows[start_idx:end_idx]:
                sel = dpg.get_item_children(r)[1][0]
                dpg.set_value(sel, True)
                self.table_selections.add(sel)
            self.table_selections.add(s)
        else:
            self.__clear_table_selections(s, a, u)
            if dpg.get_value(s):
                self.table_selections.add(s)
                self.table_last_selected = s
        u(s,a,u)

    def newWindow(self, comp=""):
        with dpg.window(
            label="Jobs",
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
        ):
            table_widths = [1,320,100,60,80,80]
            with dpg.group(horizontal=True):
                with dpg.child_window(width=700,height=600):
                    dpg.add_text("Job List")
                    dpg.add_combo(["",*[p for p in self.backend.get_profile_names()]],
                                  default_value=comp,
                                  tag=self.getKey(GUIJobs.ELEMENTS.COMPFILTER),
                                  label="Company Filter",
                                  user_data=self.getKey(GUIJobs.ELEMENTS.JOBLIST),
                                  callback=self.__filt)
                    dpg.add_combo(["",*[s.name for s in Posting.STATUS]],
                                  tag=self.getKey(GUIJobs.ELEMENTS.STATFILTER),
                                  label="Status Filter",
                                  user_data=self.getKey(GUIJobs.ELEMENTS.JOBLIST),
                                  callback=self.__filt)
                    with dpg.table(header_row=True,
                                   scrollY=True,
                                   sortable=True,
                                   tag=self.getKey(GUIJobs.ELEMENTS.JOBLIST),
                                   policy=dpg.mvTable_SizingFixedFit
                                   ):
                        dpg.add_table_column(label="", width_fixed=True, init_width_or_weight=table_widths[0])
                        for i, h in enumerate(GUIJobs.HEADINGS, 1):
                            dpg.add_table_column(label=h.name, width_fixed=True, init_width_or_weight=table_widths[i])
                        for c, ps in self.backend.historical_posts_iter():
                            if not c in self.table_company_rows:
                                self.table_company_rows[c] = []
                            for p_n, p_c in ps.items():
                                row_tag = self.getKey(GUIJobs.ELEMENTS.COMPROW, withCount=True)
                                self.table_company_rows[c].append(row_tag)
                                with dpg.table_row(tag=row_tag, filter_key=self.__filt_key(c, p_c.getStatus())):
                                    dpg.add_selectable(
                                        label="",
                                        span_columns=True,
                                        user_data=self.displayJobDesc,
                                        callback=self.__select_call)
                                    dpg.add_text(p_n)
                                    dpg.add_text(c)
                                    dpg.add_text(p_c.getStatus())
                                    dpg.add_text(p_c.getDatePulled())
                                    last_app = self.backend.get_last_applied_for_profile_by_name(c)
                                    recent_app = (not last_app is None and
                                                  last_app + self.recent_time_unit > datetime.date.today())
                                    dpg.add_text(str(recent_app))
                with dpg.group():
                    dpg.add_text("Description")
                    with dpg.child_window(width=700, height=500):
                        dpg.add_text(
                            "",
                            wrap=650,
                            tag=self.getKey(GUIJobs.ELEMENTS.JOBDESC))
                    dpg.add_button(label="View Website", callback=self.viewWebsite)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Applied", callback=self.setJobAsApplied)
                        dpg.add_button(label="Ignore", callback=self.setJobAsIgnore)
                with dpg.group(width=400):
                    dpg.add_text("Resume Management")
                    dpg.add_combo(Resume.findResumeLinks(),
                                  tag=self.getKey(GUIJobs.ELEMENTS.RESUME),
                                  )
                    dpg.add_button(label="Update Resume", callback=self.updateResume)
                    dpg.add_button(label="Create Resume", callback=self.createResume)
        if comp:
            self.__filt(None,None,self.getKey(GUIJobs.ELEMENTS.JOBLIST))

    def updateResume(self, sender, app_data, user_data):
        base_resume = dpg.get_value(self.getKey(GUIJobs.ELEMENTS.RESUME))
        if not base_resume:
            base_resume = './Resumes/main/resume.pkl'
        res = Resume.loadResume(base_resume)
        res_mod = GUIResume.fromResume(res, llm=self.llm)
        res_mod.newWindow()

    def createResume(self, sender, app_data, user_data):
        if len(self.table_selections) != 1:
            errorWindow("Please select one job posting.")
        else:
            row_data, _ = self.__get_row_info(list(self.table_selections)[0])
            base_resume = dpg.get_value(self.getKey(GUIJobs.ELEMENTS.RESUME))
            if not base_resume:
                base_resume = './Resumes/main/resume.pkl'
            job = self.backend.get_historical_posts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]]
            res = Resume.loadResume(base_resume)
            res.setOrg(row_data[GUIJobs.HEADINGS.Company.name])
            res.setJob(row_data[GUIJobs.HEADINGS.Job.name])
            res.setAITips({})
            res_mod = GUIResume.fromResumeAndPosting(res, job, llm=self.llm)
            res_mod.newWindow()

    def viewWebsite(self, sender, app_data, user_data):
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            webbrowser.open(self.backend.get_historical_posts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].getLink())
    
    def __get_row_info(self, row, bySelector=True):
        if bySelector:
            row = dpg.get_item_parent(row)
        row_kys = dpg.get_item_children(row)[1]
        row_content = dpg.get_values(row_kys)
        row_data = {}
        row_keys = {}
        for i, col in enumerate(GUIJobs.HEADINGS, 1):
            row_data[col.name] = row_content[col.value]
            row_keys[col.name] = row_kys[i]
        return row_data, row_keys

    def displayJobDesc(self, sender, app_data, user_data):
        row_data, _ = self.__get_row_info(sender)
        dpg.set_value(
            self.getKey(GUIJobs.ELEMENTS.JOBDESC),
            self.backend.get_historical_posts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].displayDescription())
  
    def setJobAsApplied(self, sender, app_data, user_data):
        comps = set([])
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            comps.add(row_data[GUIJobs.HEADINGS.Company.name])
            status = self.backend.get_historical_posts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].toggleApplied()
            dpg.set_value(
                row_keys[GUIJobs.HEADINGS.Status.name],
                status)
            dpg.configure_item(dpg.get_item_parent(row), filter_key=self.__filt_key(row_data[GUIJobs.HEADINGS.Company.name], status))
        for c in comps:
            last_app = self.backend.get_last_applied_for_profile_by_name(c)
            recent_app = (not last_app is None and
                          last_app + self.recent_time_unit > datetime.date.today())
            for r in self.table_company_rows[c]:
                row_data, row_keys = self.__get_row_info(r, bySelector=False)
                dpg.set_value(
                    row_keys[GUIJobs.HEADINGS.RecentApp.name],
                    str(recent_app))


    def setJobAsIgnore(self, sender, app_data, user_data):
        comps = set([])
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            comps.add(row_data[GUIJobs.HEADINGS.Company.name])
            status = self.backend.get_historical_posts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].toggleIgnore()
            dpg.set_value(
                row_keys[GUIJobs.HEADINGS.Status.name],
                status
                )
            dpg.configure_item(dpg.get_item_parent(row), filter_key=self.__filt_key(row_data[GUIJobs.HEADINGS.Company.name], status))
        for c in comps:
            last_app = self.backend.get_last_applied_for_profile_by_name(c)
            recent_app = (not last_app is None and
                          last_app + self.recent_time_unit > datetime.date.today())
            for r in self.table_company_rows[c]:
                row_data, row_keys = self.__get_row_info(r, bySelector=False)
                dpg.set_value(
                    row_keys[GUIJobs.HEADINGS.RecentApp.name],
                    str(recent_app))

class GUIResume(Module):
    class ELEMENTS(enum.Enum):
        RESUME = enum.auto()
        SECTION = enum.auto()
        SUBSECTION = enum.auto()
        SUBSUBSECTION = enum.auto()
        EXPERIENCE = enum.auto()
        SKILL = enum.auto()
        AISKILL = enum.auto()
        KEYTERMS = enum.auto()
    class HEADINGS(enum.Enum):
        Resume = "Resume"
        Keep = "Keep"
        Revisions = "Revisions"
        RateAndKey = "Rating and Keywords"

    def __init__(
            self,
            resume,
            posting=None,
            llm=None) -> None:
        super().__init__()
        self.resume:Resume = resume
        self.updatedResume:Resume = None
        self.posting:Posting = posting
        self.llm:LLM = llm
        self.resumeMap = {}
        self.revResumeMap = {}
        self.upResumeMap = {}
        self.revUpResumeMap = {}
        self.skillList = []
    
    def addMapping(self, key, obj):
        self.resumeMap[key] = obj
        self.revResumeMap[id(obj)] = key
    
    def mapUpdatedResume(self, orgRes:Resume, newRes:Resume):
        self.upResumeMap = {}
        self.revUpResumeMap = {}

        for orgSec, newSec in zip(orgRes.getSections(), newRes.getSections()):
            self.__updated_res_map(orgSec, newSec)
            for orgSubSec, newSubSec in zip(orgSec.getContent(), newSec.getContent()):
                self.__updated_res_map(orgSubSec, newSubSec)
                oldElms = orgSubSec.getElements()
                newElms = newSubSec.getElements()
                if isinstance(oldElms[0], str):
                    self.__updated_res_map(oldElms, newElms)
                else:
                    for orgSubSubSec, newSubSubSec in zip(oldElms, newElms):
                        self.__updated_res_map(orgSubSubSec, newSubSubSec)
                        self.__updated_res_map(orgSubSubSec.getElements(), newSubSubSec.getElements())

    def __updated_res_map(self, old, new):
        if self.isInRevMap(old):
            self.upResumeMap[id(old)] = new
            self.revUpResumeMap[id(new)] = id(old)

    def getMappedObj(self, key, convertToUpdated=True) -> Union[Section,Subsection,List[Subsection],List[str]]:
        if convertToUpdated:
            return self.upResumeMap[id(self.resumeMap[key])]
        else:
            return self.resumeMap[key]
    
    def getMappedKey(self, obj, convertToUpdated=True):
        if convertToUpdated:
            return self.revResumeMap[self.revUpResumeMap[id(obj)]]
        else:
            return self.revResumeMap[id(obj)]
    
    def isInRevMap(self, obj):
        return id(obj) in self.revResumeMap

    @classmethod
    def fromResume(cls, resume:Resume, llm:LLM=None):
        return cls(resume, llm=llm)
    
    @classmethod
    def fromResumeAndPosting(cls, resume:Resume, posting:Posting, llm:LLM=None):
        return cls(resume, posting, llm=llm)
    
    def __updateSection(self, sec):
        remove_subsecs = []
        for subsec in sec.getContent():
            elements = subsec.getElements()
            if isinstance(elements[0], str):
                self.__updateSubsec(sec, subsec, elements)
            else:
                for subsubsec in elements:
                    self.__updateSubsec(subsec, subsubsec, subsubsec.getElements())
                if not subsec.getElements():
                    remove_subsecs.append(subsec)
        for subsec in remove_subsecs:
            sec.removeSubSection(subsec)
    
    def __updateSubsec(self, sec, subsec, elements):
        tab_data = tab_keys = None
        if subsec.getType() == Subsection.Types.SKILL:
            tab_data, tab_keys = self.__get_table_info(self.getMappedKey(elements), skill=True)
        else:
            tab_data, tab_keys = self.__get_table_info(self.getMappedKey(elements))
        if self.__any_keep(tab_data):
            temp = []
            for row in tab_data:
                if row[GUIResume.HEADINGS.Keep.name]:
                    temp.append(row[GUIResume.HEADINGS.Revisions.name].replace('\n',' ').replace(' \n',' ').replace('\n ',' '))
            subsec.setElements(temp)
        else:
            sec.removeSubSection(subsec)

    def __buildResume(self):
        self.updatedResume = deepcopy(self.resume)
        self.mapUpdatedResume(self.resume, self.updatedResume)
        for i in range(self.keys.getKeyCount(GUIResume.ELEMENTS.SECTION)):
            sec_key = self.keys.getKeyAppendingCount(GUIResume.ELEMENTS.SECTION, i)
            sec = self.getMappedObj(sec_key)
            self.__updateSection(sec)

    def __any_keep(self, table):
        keep = False
        for r in table:
            if r[GUIResume.HEADINGS.Keep.name]:
                keep = True
                break
        return keep

    def __get_table_info(self, table, skill=False):
        table_data = []
        table_keys = []
        for row in dpg.get_item_children(table)[1]:
            if skill:
                row_data, row_keys = self.__get_skill_row_info(row)
                table_data.extend(row_data)
                table_keys.extend(row_keys)
            else:
                row_data, row_keys = self.__get_exp_row_info(row)
                table_data.append(row_data)
                table_keys.append(row_keys)
        return table_data, table_keys

    def __get_skill_row_info(self, row):
        row_kys = dpg.get_item_children(row)[1]
        row_data = []
        row_keys = []
        for grp in row_kys:
            item = dpg.get_item_children(grp)[1][1]
            row_data.append({GUIResume.HEADINGS.Keep.name:dpg.get_value(item),
                             GUIResume.HEADINGS.Revisions.name:dpg.get_item_label(item)})
            row_keys.append(item)
        return row_data, row_keys

    def __get_exp_row_info(self, row):
        row_kys = dpg.get_item_children(row)[1]
        row_content = dpg.get_values(row_kys)
        row_data = {}
        row_keys = {}
        for i, col in enumerate(GUIResume.HEADINGS):
            if col.name == GUIResume.HEADINGS.Keep.name:
                keep_key = dpg.get_item_children(row_kys[i])[1][1]
                row_data[col.name] = dpg.get_value(keep_key)
                row_keys[col.name] = keep_key
            else:
                row_data[col.name] = row_content[i]
                row_keys[col.name] = row_kys[i]
        return row_data, row_keys

    def newWindow(self):
        table_offset = 50
        table_widths = [550,50,550,550]
        exp_row_height = 50
        skill_row_height = 12
        skill_num_cols = 5
        wrap_pix_per_char = 7
        def addContent(subsecs:List[Subsection]):
            for ss in subsecs:
                if ss.getType() == Subsection.Types.ORGANIZATION:
                    sec_key = self.getKey(GUIResume.ELEMENTS.SUBSECTION, withCount=True)
                    dpg.add_text(ss.getSubject(), tag=sec_key)
                    self.addMapping(sec_key, ss)
                    addContent(ss.getElements())
                elif (ss.getType() == Subsection.Types.POSITION or
                      ss.getType() == Subsection.Types.PROJECT or
                      ss.getType() == Subsection.Types.SCHOOL):
                    sec_key = self.getKey(GUIResume.ELEMENTS.SUBSUBSECTION, withCount=True)
                    dpg.add_text('\t'+ss.getSubject(), tag=sec_key)
                    self.addMapping(sec_key, ss)
                    sec_key = self.getKey(GUIResume.ELEMENTS.EXPERIENCE, withCount=True)
                    self.addMapping(sec_key, ss.getElements())
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=table_offset)
                        with dpg.table(tag=sec_key, header_row=False):
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[0])
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[1])
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[2])
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[3])
                            for e in ss.getElements():
                                with dpg.table_row():
                                    dpg.add_input_text(
                                        default_value=textWrapper(e,table_widths[0]//wrap_pix_per_char),
                                        multiline=True,
                                        readonly=True,
                                        width=table_widths[0],
                                        height=exp_row_height)
                                    with dpg.group(horizontal=True):
                                        dpg.add_spacer(width=(table_widths[1]-table_widths[1]*2/3)/2)
                                        dpg.add_checkbox(default_value=True)
                                    dpg.add_input_text(
                                        default_value=textWrapper(e,table_widths[2]//wrap_pix_per_char),
                                        multiline=True,
                                        width=table_widths[2],
                                        height=exp_row_height)
                                    dpg.add_input_text(
                                        default_value="",
                                        multiline=True,
                                        width=table_widths[3],
                                        height=exp_row_height)
                elif ss.getType() == Subsection.Types.SKILL:
                    sec_key = self.getKey(GUIResume.ELEMENTS.SUBSECTION, withCount=True)
                    dpg.add_text(ss.getSubject(), tag=sec_key)
                    self.addMapping(sec_key, ss)

                    if isinstance(ss.getElements()[0], str):
                        sec_key = self.getKey(GUIResume.ELEMENTS.SKILL, withCount=True)
                        self.addMapping(sec_key, ss.getElements())
                        with dpg.group(horizontal=True):
                            dpg.add_spacer(width=table_offset)
                            with dpg.table(tag=sec_key, header_row=False):
                                for i in range(skill_num_cols):
                                    dpg.add_table_column()
                                row = None
                                for i, e in enumerate(ss.getElements()):
                                    if i % skill_num_cols == 0:
                                        row = dpg.add_table_row()
                                    with dpg.group(horizontal=True, parent=row):
                                        dpg.add_spacer(width=1)
                                        self.skillList.append(dpg.add_selectable(label=e,
                                                        height=skill_row_height,
                                                        default_value=True))
                    else:
                        for sss in ss.getElements():
                            sec_key = self.getKey(GUIResume.ELEMENTS.SUBSUBSECTION, withCount=True)
                            dpg.add_text("\t"+sss.getSubject(), tag=sec_key)
                            self.addMapping(sec_key, sss)

                            sec_key = self.getKey(GUIResume.ELEMENTS.SKILL, withCount=True)
                            self.addMapping(sec_key, sss.getElements())
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=table_offset)
                                with dpg.table(tag=sec_key, header_row=False):
                                    for i in range(skill_num_cols):
                                        dpg.add_table_column()
                                    row = None
                                    for i, e in enumerate(sss.getElements()):
                                        if i % skill_num_cols == 0:
                                            row = dpg.add_table_row()
                                        with dpg.group(horizontal=True, parent=row):
                                            dpg.add_spacer(width=1)
                                            self.skillList.append(dpg.add_selectable(label=e,
                                                            height=skill_row_height,
                                                            default_value=True))
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()
        with dpg.window(
            label="Resume - {} - {}".format(self.resume.getOrg(),self.resume.getJob()),
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            modal=True,
            height=viewport_height,
            width=viewport_width,
        ):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=table_offset)
                with dpg.table(header_row=False):
                    dpg.add_table_column(width_fixed=True, init_width_or_weight=800)
                    dpg.add_table_column(width_stretch=True, init_width_or_weight=0.0)
                    dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[3])
                    with dpg.table_row():
                        dpg.add_text(wrap=800, tag=self.getKey(GUIResume.ELEMENTS.KEYTERMS))
                        dpg.add_spacer(height=80)
                        dpg.add_button(label="Get AI Tips", callback=self.runAI, width=-1)                        
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=table_offset)
                prev_table_width = 0
                prev_text_width = 0
                for i, h in enumerate(GUIResume.HEADINGS):
                    t = h.value
                    w = len(t)*wrap_pix_per_char
                    dpg.add_spacer(width=(prev_table_width+table_widths[i]-prev_text_width-w)//2)
                    dpg.add_text(t)
                    prev_table_width = table_widths[i]
                    prev_text_width = w
            with dpg.child_window(height=770, tag=self.getKey(GUIResume.ELEMENTS.RESUME)):
                for sec in self.resume.getSections():
                    sec_key = self.getKey(GUIResume.ELEMENTS.SECTION, True)
                    dpg.add_text(sec.getTitle(), tag=sec_key)
                    self.addMapping(sec_key, sec)
                    if sec.getTitle() == "Skills":
                        with dpg.table(header_row=False):
                            dpg.add_table_column(width_stretch=True, init_width_or_weight=0.0)
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=40)
                            dpg.add_table_column(width_fixed=True, init_width_or_weight=550)
                            with dpg.table_row():
                                with dpg.group():
                                    addContent(sec.getContent())
                                dpg.add_spacer()
                                sec_key = self.getKey(GUIResume.ELEMENTS.AISKILL)
                                with dpg.table(tag=sec_key):
                                    dpg.add_table_column(label="Top 20 Skills")
                    else:
                        addContent(sec.getContent())
            with dpg.group(horizontal=True):
                dpg.add_button(label="Update Resume", callback=self.saveJSON)
                dpg.add_button(label="Generate PDF", callback=self.savePDF)
    
    def saveJSON(self, sender, app_data, user_data):
        self.__buildResume()
        self.updatedResume.saveResume()

    def savePDF(self, sender, app_data, user_data):
        if self.updatedResume:
            pdf().fromResume(self.updatedResume)
        else:
            pdf().fromResume(self.resume)

    def runAI(self, sender, app_data, user_data):
        if self.posting:
            try:
                tips = self.llm.getTips(
                    self.resume,
                    '{}\n{}'.format(self.posting.getTitle(),self.posting.getDesc()))
                self.resume.setAITips(tips)
                dpg.set_value(
                    self.getKey(GUIResume.ELEMENTS.KEYTERMS),
                    "Job Description Key Terms:\n{}".format(tips["Key Terms"].replace('- ','').replace('\n',', ')))
                tip_idx = 0
                for i in range(self.keys.getKeyCount(GUIResume.ELEMENTS.EXPERIENCE)):
                    if tip_idx >= len(tips["Experience"]):
                        break
                    table_tag = self.keys.getKeyAppendingCount(GUIResume.ELEMENTS.EXPERIENCE, i)
                    for row in dpg.get_item_children(table_tag)[1]:
                        if tip_idx >= len(tips["Experience"]):
                            break
                        row_data, row_keys = self.__get_exp_row_info(row)
                        if tips["Experience"][tip_idx]['rating'] > 5:
                            dpg.set_value(
                                row_keys[GUIResume.HEADINGS.Keep.name],
                                True)
                        else:
                            dpg.set_value(
                                row_keys[GUIResume.HEADINGS.Keep.name],
                                False)
                        dpg.set_value(
                            row_keys[GUIResume.HEADINGS.RateAndKey.name],
                            "{:.2f} | {}".format(
                                tips["Experience"][tip_idx]['rating'],
                                ",".join(tips["Experience"][tip_idx]['keywords'])))
                        tip_idx += 1
                top20 = self.resume.getTopSkills()
                for skl in self.skillList:
                    dpg.set_value(skl, False)
                for i, skl in top20:
                    with dpg.table_row(parent=self.getKey(GUIResume.ELEMENTS.AISKILL)):
                        dpg.add_text("{} | {:.2f} | {}".format(dpg.get_item_label(self.skillList[i]), skl["rating"], skl["keywords"]))
                    dpg.set_value(self.skillList[i], True)
            except Exception as inst:
                errorWindow("Something went wrong invoking the AI model.\n{}:{}\n{}".format(type(inst), inst, traceback.format_exc()))
        else:
            errorWindow("Currently Updating existing resume. No Job description to compare to.\nClose window and select 'Create Resume' instead")