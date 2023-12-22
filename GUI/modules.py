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
    @abc.abstractmethod
    def newWindow(self):
        pass
    def proposePosition(self, offset=7):
        pos = dpg.get_item_pos(dpg.get_active_window())
        pos[0] += offset
        pos[1] += offset
        return pos
    def getKey(self, k, withCount=False):
        return self.keys.getKey(k, withCount)

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
        with dpg.window(tag=tag):
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
        #TODO
        profile_name = dpg.get_value(self.getKey(GUIMain.ELEMENTS.PROFILES))
        prof_mod = GUIProfile.fromProfile(self.portfolio.getProfiles()[profile_name])
        prof_mod.newWindow()

        # for p in values[GUI.MAINELEMENTS.PROFILES]:
        #     w = self.profileWindow(p)
        #     if p != GUI.NEWPROFILE:
        #         self.refreshSearchConfigVisual(w, self.portfolio.getProfiles()[p])

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
        RETTYPE = ["HTML", "JSON"]
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
    
    def newWindow(self):
        with dpg.window(pos=self.proposePosition()):
            with dpg.group(horizontal=True):
                with dpg.group(width=200):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Profile Name:")
                        dpg.add_input_text()
                    dpg.add_text("Sample Request")
                    dpg.add_input_text(multiline=True)
                with dpg.group(width=200):
                    dpg.add_text("Method Configuration")
                    dpg.add_text("Expected Reponses-")
                    with dpg.group(horizontal=True):
                        dpg.add_text("  of Search:")
                        dpg.add_radio_button(
                            GUIProfile.OPTIONS.RETTYPE,
                            horizontal=True,
                            tag=self.getKey(GUIProfile.ELEMENTS.SEARCHRETTYPE))
                    with dpg.group(horizontal=True):
                        dpg.add_text("  of Descriptions:")
                        dpg.add_radio_button(
                            GUIProfile.OPTIONS.RETTYPE,
                            horizontal=True,
                            tag=self.getKey(GUIProfile.ELEMENTS.DESCRETTYPE))
                    dpg.add_text("Render Required-")
                    with dpg.group(horizontal=True):
                        dpg.add_text("  of Search:")
                        dpg.add_radio_button(
                            GUIProfile.OPTIONS.RENREQ,
                            horizontal=True,
                            tag=self.getKey(GUIProfile.ELEMENTS.SEARCHRENREQ))
                    with dpg.group(horizontal=True):
                        dpg.add_text("  of Descriptions:")
                        dpg.add_radio_button(
                            GUIProfile.OPTIONS.RENREQ,
                            horizontal=True,
                            tag=self.getKey(GUIProfile.ELEMENTS.DESCRENREQ))
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
                            dpg.add_input_text(tag=self.getKey(GUIProfile.ELEMENTS.JOBKEYID))
                            dpg.add_input_text(
                                default_value="page",
                                tag=self.getKey(GUIProfile.ELEMENTS.PAGEKEYID))
                            dpg.add_input_text(
                                default_value="type.class; e.g. div.main",
                                tag=self.getKey(GUIProfile.ELEMENTS.HTMLTITLEKEY))
                            dpg.add_input_text(
                                default_value="type.class; e.g. div.main",
                                tag=self.getKey(GUIProfile.ELEMENTS.HTMLDESCKEY))
                    
        

class GUIJobs(Module):
    pass