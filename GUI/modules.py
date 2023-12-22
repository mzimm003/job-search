import dearpygui.dearpygui as dpg
import webbrowser
from Search.profile import (
    Profile,
    Portfolio
)
from typing import (
    List,
    Dict,
    Type
)
import abc
import enum

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
            dpg.remove_alias(a)

class Keys:
    def __init__(self, cls) -> None:
        self.counts = {k:0 for k in cls.ELEMENTS}
        self.cls = cls
    def getKey(self, k, withCount=False):
        key = str(self.cls)+str(k)
        if withCount:
            ret = self.counts[k]
            self.counts[key] += 1
            return str((key, ret))
        else:
            return key

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
            portfolio,
            ) -> None:
        super().__init__()
        self.portfolio:Portfolio = portfolio
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
                        [k for k in self.portfolio.getProfiles().keys()],
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
                    dpg.add_text("", wrap=300)
        dpg.set_primary_window(tag, True)

    def openProfile(self, sender, app_data, user_data):
        profile_name = dpg.get_value(self.getKey(GUIMain.ELEMENTS.PROFILES))
        prof_mod = GUIProfile.fromProfile(self.portfolio.getProfiles()[profile_name])
        prof_mod.newWindow()

    def openJobs(self, sender, app_data, user_data):
        #TODO
        Jobs()

    def getAllNewJobs(self, sender, app_data, user_data):
        #TODO
        windowUpdate = ''
        numNewJobs = 0 
        for n, p in self.portfolio.getProfiles().items():
            self.getCurrentJobs(values=values, window=None, profile=p, updateProfWin=False)
            numNewJobs += len(p.currentPosts)
            windowUpdate += '\n{}:\n\t'.format(p.name)
            windowUpdate += '\n\t'.join(p.currentPosts.keys())
        window[GUI.MAINELEMENTS.NEWJOBS].update('{} new jobs found:{}'.format(numNewJobs, windowUpdate))

    def getCurrentJobs(self, values, window, profile, updateProfWin=True):
        #TODO
        self.portfolio.getNewJobsByProfile(profile)
        if updateProfWin:
            window[GUI.PROFILEELEMENTS.JOBSTATUSUPDATE].update('{} new jobs found:\n{}'.format(len(profile.currentPosts), '\n'.join(profile.currentPosts.keys())))

class GUIProfile(Module):
    class OPTIONS:
        RETTYPE = ["html", "json"]
        RENREQ = ["No", "Yes"]
    class ELEMENTS(enum.Enum):
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
        CSSSELECTORHELP = enum.auto()
        CSSSELECTORHELP1 = enum.auto()
        PROFILENAME = enum.auto()

        #Job Elements
        JOBSTATUSUPDATE = enum.auto()
        GETCURRENTJOBS = enum.auto()
        JOBSDETAIL = enum.auto()
    def __init__(
            self,
            profile) -> None:
        super().__init__()
        self.profile:Profile = profile
    
    @classmethod
    def fromProfile(cls, profile:Profile):
        return cls(profile)
    
    def getKey(self, k, withCount=False):
        k = self.profile.getName()+str(k)
        return super().getKey(k, withCount)
    
    def newWindow(self):
        column_widths = [200,200,-1]
        with dpg.window(pos=self.proposePosition(), on_close=self.cleanAliases):
            with dpg.group():
                with dpg.group(horizontal=True):
                    with dpg.group(width=column_widths[0]):
                        with dpg.group(horizontal=True):
                            t = dpg.add_text("Profile Name:")
                            dpg.add_input_text(default_value=self.profile.getName())
                        dpg.add_text("Sample Request")
                        dpg.add_input_text(multiline=True)
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
                                        callback=lambda:webbrowser.open('https://www.w3schools.com/cssref/css_selectors.php'),
                                        small=True)
                                with dpg.group(horizontal=True):
                                    dpg.add_text("Job Desc HTML Element")
                                    dpg.add_button(
                                        label="(help)",
                                        callback=lambda:webbrowser.open('https://www.w3schools.com/cssref/css_selectors.php'),
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
                        dpg.add_button(label="Peek Links", tag=self.getKey(GUIProfile.ELEMENTS.PEEKLINKS))
                        dpg.add_text("Job Desc HTML Element Help")
                        dpg.add_input_text(tag=self.getKey(GUIProfile.ELEMENTS.DESCRIPTION), multiline=True, readonly=True)
                        dpg.add_button(label="Peek Description", tag=self.getKey(GUIProfile.ELEMENTS.PEEKDESC))
                with dpg.group():
                    dpg.add_button(label="Commit Changes", tag=self.getKey(GUIProfile.ELEMENTS.ADDSEARCH))
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(
                            tag=self.getKey(GUIProfile.ELEMENTS.SEARCHPHRASES),
                            width=150, height=60,
                            multiline=True,
                            default_value=self.profile.getSearch().getSearchPhrases(asString=True))
                        dpg.add_button(label="Commit Phrases", tag=self.getKey(GUIProfile.ELEMENTS.COMMITPHRASES))
                
        # search_phrase_layout = sg.Col([
        #     [sg.Multiline(size=(25,8), key=GUI.PROFILEELEMENTS.SEARCHPHRASES),sg.Button('Commit Phrases', key=GUI.PROFILEELEMENTS.COMMITPHRASES)],
        #     ], expand_x=True, expand_y=True)

        # #JOBS LAYOUT

        # #TAB LAYOUT
        # search_panel_layout = [
        #     [config_layout, method_layout,peek_layout],
        #     [sg.Button('Commit Changes', key=GUI.PROFILEELEMENTS.ADDSEARCH)],
        #     [search_phrase_layout]
        #     ]
        # job_panel_layout = [
        #     [sg.Button('Find Current Jobs', key=GUI.PROFILEELEMENTS.GETCURRENTJOBS)],
        #     [sg.Multiline(size=(70,20),key=GUI.PROFILEELEMENTS.JOBSTATUSUPDATE)],
        #     [sg.Button('View Jobs', key=GUI.PROFILEELEMENTS.JOBSDETAIL)]
        # ]
        # tabs = sg.TabGroup([[
        #     sg.Tab('Config', search_panel_layout),
        #     sg.Tab('Jobs', job_panel_layout)]], expand_x=True, expand_y=True)
                    
        

class GUIJobs(Module):
    pass