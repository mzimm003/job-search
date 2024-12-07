from jobsearch.gui.module import Module
import enum
import dearpygui.dearpygui as dpg

class GUIBasicInfo(Module):
    class ELEMENTS(enum.Enum):
        NAME = enum.auto()
        EMAIL = enum.auto()
        PHONE = enum.auto()
        LOCATION = enum.auto()
        LINKEDINLINK = enum.auto()
        GITHUBLINK = enum.auto()
        WEBSITE = enum.auto()
    
    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)

    def newWindow(self):
        with dpg.tab(label="Basic Information"):
            dpg.add_input_text(
                label="Name",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.NAME))
            dpg.add_input_text(
                label="Email",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.EMAIL))
            dpg.add_input_text(
                label="Phone",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.PHONE))
            dpg.add_input_text(
                label="Location",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.LOCATION))
            dpg.add_input_text(
                label="LinkedIn Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.LINKEDINLINK))
            dpg.add_input_text(
                label="Github Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.GITHUBLINK))
            dpg.add_input_text(
                label="Website Link",
                tag=self.getKey(GUIBasicInfo.ELEMENTS.WEBSITE))
                
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