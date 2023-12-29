import dearpygui.dearpygui as dpg
import webbrowser
from Search.transforms import Transform, Request
from Search.profile import (
    Profile,
    Portfolio,
    Posting
)
from Search.search import Search
from Resumes.resume import Resume, Subsection, ResumeRevision
from Resumes.llm import LLM
from typing import (
    List,
    Dict,
    Type
)
from Search.utility import errorWindow, textWrapper
import abc
import enum
import pickle

class Module(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        self.keys = Keys(self.__class__)
        self.aliasesCreated = []
    @abc.abstractmethod
    def newWindow(self):
        pass
    def proposePosition(self, offset=7):
        pos = dpg.get_item_pos(dpg.get_active_window())
        pos[0] += offset
        pos[1] += offset
        return pos
    def getKey(self, k, withCount=False):
        key = self.keys.getKey(k, withCount)
        self.aliasesCreated.append(key)
        return key
    def cleanAliases(self):
        for a in self.aliasesCreated:
            if dpg.does_alias_exist(a):
                dpg.remove_alias(a)

class Keys:
    def __init__(self, cls) -> None:
        self.counts = {k:0 for k in cls.ELEMENTS}
        self.cls = cls
    def getKey(self, k, withCount=False):
        key = str(self.cls)+str(k)
        if withCount:
            ret = self.counts[k]
            self.counts[k] += 1
            return str((key, ret))
        else:
            return key
    def getKeyAppendingCount(self, k, count):
        key = str(self.cls)+str(k)
        return str((key, count))
    def getKeyCount(self, k):
        return self.counts[k]

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
            portfolio=None,
            llm=None
            ) -> None:
        super().__init__()
        self.portfolio:Portfolio = portfolio
        self.llm = llm
        # self.modules:Dict[str,List[Module]] = {}

    # def openModule(self, mod:Type[Module], **kwargs):
    #     new_module = mod(**kwargs)

    #     self.modules[new_module.getName()] = 

    def newWindow(self):
        tag = self.getKey(GUIMain.ELEMENTS.WINDOW)
        with dpg.window(tag=tag, on_close=self.cleanAliases):
            with dpg.group(horizontal=True):
                with dpg.group(width=500):
                    dpg.add_text("Profiles")
                    dpg.add_listbox(
                        [k for k in self.portfolio.getProfileNames()],
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
        prof_mod = GUIProfile.fromProfileAndPortfolio(self.portfolio.selectProfileByName(profile_name), self.portfolio, llm=self.llm)
        prof_mod.newWindow()

    def openJobs(self, sender, app_data, user_data):
        job_mod = GUIJobs.fromPortfolio(self.portfolio, llm=self.llm)
        job_mod.newWindow()

    def getAllNewJobs(self, sender, app_data, user_data):
        windowUpdate = ''
        numNewJobs = 0 
        for p in self.portfolio.getProfiles().values():
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
        PROFILENAME = enum.auto()

        #Job Elements
        JOBSTATUSUPDATE = enum.auto()
        GETCURRENTJOBS = enum.auto()
        JOBSDETAIL = enum.auto()
    def __init__(
            self,
            profile,
            portfolio,
            llm=None) -> None:
        super().__init__()
        self.profile:Profile = profile
        self.portfolio:Portfolio = portfolio
        self.llm = llm
    
    @classmethod
    def fromProfileAndPortfolio(cls, profile:Profile, portfolio:Portfolio, llm:LLM=None):
        return cls(profile, portfolio, llm=llm)
    
    def getKey(self, k, withCount=False):
        k = self.profile.getName()+str(k)
        return super().getKey(k, withCount)
    
    def newWindow(self):
        column_widths = [200,200,-1]
        with dpg.window(
            label=self.profile.getName().upper(),
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            tag=self.getKey(GUIProfile.ELEMENTS.WINDOW)):
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
                                        default_value=self.profile.getSearch().getJobListRetType())
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
                                dpg.add_listbox(tag=self.getKey(GUIProfile.ELEMENTS.LINKS))
                                dpg.add_button(
                                    label="Peek Links",
                                    tag=self.getKey(GUIProfile.ELEMENTS.PEEKLINKS),
                                    callback=self.peekLinks)
                                dpg.add_text("Job Desc HTML Element Help")
                                dpg.add_input_text(
                                    tag=self.getKey(GUIProfile.ELEMENTS.DESCRIPTION),
                                    multiline=True,
                                    readonly=True)
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

    def cssSelectorHelp(self, sender, app_data, user_data):
        webbrowser.open('https://www.w3schools.com/cssref/css_selectors.php')

    def peekDesc(self, sender, app_data, user_data):
        if self.profile.getName() == Profile.NEWPROFILE:
            errorWindow("Must first commit search to create profile.")
        else:
            dpg.set_value(self.getKey(GUIProfile.ELEMENTS.DESCRIPTION), self.profile.samplePosts())

    def openJobDetail(self, sender, app_data, user_data):
        job_mod = GUIJobs.fromPortfolio(self.portfolio, llm=self.llm)
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

    def searchPhraseWindow(self):
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
        wrapped_text = textWrapper(
            dpg.get_value(self.getKey(GUIProfile.ELEMENTS.MLSEARCHHEADER)),
            wrap_len=65)

        with dpg.window(label="Search Phrase", modal=True, tag="temp_win"):
            dpg.add_text("Please identify the\nsearch phrase in the url:")
            dpg.add_input_text(
                default_value=wrapped_text,
                width=500, height=70,
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
            dpg.configure_item(self.getKey(GUIProfile.ELEMENTS.LINKS), items=links)

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
                self.searchPhraseWindow()
    
    def __updatePortfolio(self, profile:Profile, renameProfile:bool=False):
        window_to_close = self.getKey(GUIProfile.ELEMENTS.WINDOW)
        if renameProfile:
            self.portfolio.renameProfile(profile, dpg.get_value(self.getKey(GUIProfile.ELEMENTS.PROFILENAME)))
        else:
            self.portfolio.addProfile(profile)
        dpg.configure_item(GUIMain().getKey(GUIMain.ELEMENTS.PROFILES), items=[k for k in self.portfolio.getProfileNames()])
        new_prof = GUIProfile.fromProfileAndPortfolio(profile=profile, portfolio=self.portfolio)
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
        # GETTIPS = enum.auto()
    class HEADINGS(enum.Enum):
        Job = enum.auto()
        Company = enum.auto()
        Status = enum.auto()
        Date = enum.auto()

    def __init__(
            self,
            portfolio,
            llm=None) -> None:
        super().__init__()
        self.portfolio:Portfolio = portfolio
        self.table_selections = set([])
        self.llm = llm
    
    @classmethod
    def fromPortfolio(cls, portfolio:Portfolio, llm:LLM=None):
        return cls(portfolio, llm=llm)
    
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
        self.__clear_table_selections(s, a, u)
        if dpg.get_value(s):
            self.table_selections.add(s)
        u(s,a,u)

    def newWindow(self, comp=""):
        with dpg.window(
            label="Jobs",
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
        ):
            table_widths = [1,320,100,60,80]
            with dpg.group(horizontal=True):
                with dpg.child_window(width=600,height=600):
                    dpg.add_text("Job List")
                    dpg.add_combo(["",*[p for p in self.portfolio.getProfiles()]],
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
                        for c, ps in self.portfolio.getHistoricalPosts().items():
                            for p_n, p_c in ps.items():
                                with dpg.table_row(filter_key=self.__filt_key(c, p_c.getStatus())):
                                    dpg.add_selectable(
                                        label="",
                                        span_columns=True,
                                        user_data=self.displayJobDesc,
                                        callback=self.__select_call)
                                    dpg.add_text(p_n)
                                    dpg.add_text(c)
                                    dpg.add_text(p_c.getStatus())
                                    dpg.add_text(p_c.getDatePulled())
                        # dpg.add_mouse_down_handler()
                        # dpg.add_mouse_release_handler()
                        # dpg.add_mouse_drag_handler()
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
            job = self.portfolio.getHistoricalPosts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]]
            res = Resume.loadResume(base_resume)
            res.setOrg(row_data[GUIJobs.HEADINGS.Company.name])
            res.setJob(row_data[GUIJobs.HEADINGS.Job.name])
            res_mod = GUIResume.fromResumeAndPosting(res, job, llm=self.llm)
            res_mod.newWindow()

    def viewWebsite(self, sender, app_data, user_data):
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            webbrowser.open(self.portfolio.getHistoricalPosts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].getLink())
    
    def __get_row_info(self, row):
        row_kys = dpg.get_item_children(dpg.get_item_parent(row))[1]
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
            self.portfolio.getHistoricalPosts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].displayDescription())
  
    def setJobAsApplied(self, sender, app_data, user_data):
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            dpg.set_value(
                row_keys[GUIJobs.HEADINGS.Status.name],
                self.portfolio.getHistoricalPosts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].toggleApplied())

    def setJobAsIgnore(self, sender, app_data, user_data):
        for row in self.table_selections:
            row_data, row_keys = self.__get_row_info(row)
            dpg.set_value(
                row_keys[GUIJobs.HEADINGS.Status.name],
                self.portfolio.getHistoricalPosts()[row_data[GUIJobs.HEADINGS.Company.name]][row_data[GUIJobs.HEADINGS.Job.name]].toggleIgnore())

class GUIResume(Module):
    class ELEMENTS(enum.Enum):
        SECTION = enum.auto()
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
        self.posting:Posting = posting
        self.llm:LLM = llm
        self.resumeMap = {}
    
    def addMapping(self, key, obj):
        self.resumeMap[key] = obj
    
    @classmethod
    def fromResume(cls, resume:Resume, llm:LLM=None):
        return cls(resume, llm=llm)
    
    @classmethod
    def fromResumeAndPosting(cls, resume:Resume, posting:Posting, llm:LLM=None):
        return cls(resume, posting, llm=llm)

    def __get_row_info(self, row):
        row_kys = dpg.get_item_children(row)[1]
        row_content = dpg.get_values(row_kys)
        row_data = {}
        row_keys = {}
        for i, col in enumerate(GUIResume.HEADINGS):
            row_data[col.name] = row_content[i]
            row_keys[col.name] = row_kys[i]
        return row_data, row_keys

    def newWindow(self):
        table_offset = 50
        table_widths = [450,50,450,450]
        row_height = 50
        wrap_pix_per_char = 7
        def addContent(subsecs:List[Subsection]):
            for ss in subsecs:
                if ss.getType() == Subsection.Types.ORGANIZATION:
                    dpg.add_text(ss.getSubject())
                    addContent(ss.getElements())
                elif (ss.getType() == Subsection.Types.POSITION or
                      ss.getType() == Subsection.Types.PROJECT or
                      ss.getType() == Subsection.Types.SCHOOL):
                    dpg.add_text('\t'+ss.getSubject())
                    sec_key = self.getKey(GUIResume.ELEMENTS.SECTION, withCount=True)
                    self.addMapping(sec_key, ss)
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
                                        height=row_height)
                                    dpg.add_checkbox(default_value=True)
                                    dpg.add_input_text(
                                        default_value=textWrapper(e,table_widths[2]//wrap_pix_per_char),
                                        multiline=True,
                                        width=table_widths[2],
                                        height=row_height)
                                    dpg.add_input_text(
                                        default_value="",
                                        multiline=True,
                                        width=table_widths[3],
                                        height=row_height)
                elif ss.getType() == Subsection.Types.SKILL:
                    dpg.add_text(ss.getSubject())
                    if isinstance(ss.getElements()[0], str):
                        sec_key = self.getKey(GUIResume.ELEMENTS.SECTION, withCount=True)
                        self.addMapping(sec_key, ss)
                        with dpg.group(horizontal=True):
                            dpg.add_spacer(width=table_offset)
                            with dpg.table(tag=sec_key, header_row=False):
                                dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[0])
                                dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[1])
                                dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[2])
                                dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[3])
                                with dpg.table_row():
                                    dpg.add_input_text(
                                        default_value=textWrapper(','.join(ss.getElements()),table_widths[0]//wrap_pix_per_char),
                                        multiline=True,
                                        readonly=True,
                                        width=table_widths[0],
                                        height=row_height)
                                    dpg.add_checkbox(default_value=True)
                                    dpg.add_input_text(
                                        default_value=textWrapper(','.join(ss.getElements()),table_widths[2]//wrap_pix_per_char),
                                        multiline=True,
                                        width=table_widths[2],
                                        height=row_height)
                                    dpg.add_input_text(
                                        default_value="",
                                        multiline=True,
                                        width=table_widths[3],
                                        height=row_height)
                    else:
                        for sss in ss.getElements():
                            dpg.add_text("\t"+sss.getSubject())
                            sec_key = self.getKey(GUIResume.ELEMENTS.SECTION, withCount=True)
                            self.addMapping(sec_key, sss)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=table_offset)
                                with dpg.table(tag=sec_key, header_row=False):
                                    dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[0])
                                    dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[1])
                                    dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[2])
                                    dpg.add_table_column(width_fixed=True, init_width_or_weight=table_widths[3])
                                    with dpg.table_row():
                                        dpg.add_input_text(
                                            default_value=textWrapper(','.join(sss.getElements()),table_widths[0]//wrap_pix_per_char),
                                            multiline=True,
                                            readonly=True,
                                            width=table_widths[0],
                                            height=row_height)
                                        dpg.add_checkbox(default_value=True)
                                        dpg.add_input_text(
                                            default_value=textWrapper(','.join(sss.getElements()),table_widths[2]//wrap_pix_per_char),
                                            multiline=True,
                                            width=table_widths[2],
                                            height=row_height)
                                        dpg.add_input_text(
                                            default_value="",
                                            multiline=True,
                                            width=table_widths[3],
                                            height=row_height)
        with dpg.window(
            label="Resume - {} - {}".format(self.resume.getOrg(),self.resume.getJob()),
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            modal=True,
            height=920,
            width=1600
        ):
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=table_offset)
                    dpg.add_spacer(width=table_widths[0]+table_widths[1]+table_widths[2])
                    with dpg.group(width=table_widths[3]):
                        dpg.add_button(label="Get AI Tips", callback=self.runAI)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=table_offset)
                    t = "Resume"
                    w1 = len(t)*wrap_pix_per_char
                    dpg.add_spacer(width=(table_widths[0]-w1)//2)
                    dpg.add_text(t)
                    t = "Keep"
                    w2 = len(t)*wrap_pix_per_char
                    dpg.add_spacer(width=(table_widths[0]+table_widths[1]-w1-w2)//2)
                    dpg.add_text(t)
                    t = "Revisions"
                    w3 = len(t)*wrap_pix_per_char
                    dpg.add_spacer(width=(table_widths[1]+table_widths[2]-w2-w3)//2)
                    dpg.add_text(t)
                    t = "Rating and Keywords"
                    w4 = len(t)*wrap_pix_per_char
                    dpg.add_spacer(width=(table_widths[2]+table_widths[3]-w3-w4)//2)
                    dpg.add_text(t)
                with dpg.child_window(height=800):
                    for sec in self.resume.getSections():
                        dpg.add_text(sec.getTitle())
                        addContent(sec.getContent())
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Update Resume", callback=self.saveJSON)
                    dpg.add_button(label="Generate PDF", callback=self.savePDF)
    
    def saveJSON(self, sender, app_data, user_data):
        pass

    def savePDF(self, sender, app_data, user_data):
        pass

    def runAI(self, sender, app_data, user_data):
        if self.posting:
            tips = self.llm.getTips(
                self.resume.asString(bulletsOnly=True, skipEdu=True, lineNums=True),
                '{}\n{}'.format(self.posting.getTitle(),self.posting.getDesc()))
            tip_idx = 0
            for i in range(self.keys.getKeyCount(GUIResume.ELEMENTS.SECTION)):
                if tip_idx >= len(tips):
                    break
                table_tag = self.keys.getKeyAppendingCount(GUIResume.ELEMENTS.SECTION, i)
                for row in dpg.get_item_children(table_tag)[1]:
                    if tip_idx >= len(tips):
                        break
                    row_data, row_keys = self.__get_row_info(row)
                    dpg.set_value(
                        row_keys[GUIResume.HEADINGS.RateAndKey.name],
                        "{:.2f} | {}".format(
                            tips[tip_idx]['rating'],
                            ",".join(tips[tip_idx]['keywords'])))
                    tip_idx += 1
        else:
            errorWindow("Currently Updating existing resume. No Job description to compare to.\nClose window and select 'Create Resume' instead")