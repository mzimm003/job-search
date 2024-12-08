from jobsearch.gui.module import Module
import enum
import dearpygui.dearpygui as dpg

class GUIUserProfileUpdateModule(Module):
    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)

    def update_profile(self, )

class GUIBasicInfo(GUIUserProfileUpdateModule):
    class ELEMENTS(enum.Enum):
        NAME = enum.auto()
        EMAIL = enum.auto()
        PHONE = enum.auto()
        LOCATION = enum.auto()
        LINKEDINLINK = enum.auto()
        GITHUBLINK = enum.auto()
        WEBSITE = enum.auto()
        SUMMARY = enum.auto()

    def newWindow(self):
        with dpg.tab(label="Basic Information"):
            dpg.add_input_text(
                label="Name",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.NAME),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Email",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.EMAIL),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Phone",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.PHONE),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Location",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.LOCATION),
                callback=self.update_profile)
            dpg.add_input_text(
                label="LinkedIn Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.LINKEDINLINK),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Github Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.GITHUBLINK),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Website Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.WEBSITE),
                callback=self.update_profile)
            dpg.add_input_text(
                label="Summary",
                multiline=True,
                height=250,
                tag=self.getKey(GUIBasicInfo.ELEMENTS.SUMMARY),
                callback=self.update_profile)
                
class GUIUserProfile(Module):
    class ELEMENTS(enum.Enum):
        ...
    
    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)

    def newWindow(self):
        with dpg.tab(label="User Profile"):
            with dpg.tab_bar():
                GUIBasicInfo(backend=self.backend).newWindow()