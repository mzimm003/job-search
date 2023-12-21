import dearpygui.dearpygui as dpg
import abc
import enum

class Module(abc.ABC):
    @abc.abstractmethod
    def newWindow(self):
        pass
class Keys:
    def __init__(self, cls) -> None:
        self.counts = {k:0 for k in cls.ELEMENTS}
    def getKey(self, k):
        ret = self.counts[k]
        self.counts[k] += 1
        return str((k, ret))

class Main(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        PROFILES = enum.auto()
        JOBSDETAIL = enum.auto()
        ALLNEWJOBS = enum.auto()
        NEWJOBS = enum.auto()
        OPENPROFILE = enum.auto()
    
    def __init__(
            self,
            profiles,
            ) -> None:
        super().__init__()
        self.keys = Keys(self.__class__)
        self.profiles = profiles

    def newWindow(self):
        tag = self.keys.getKey(Main.ELEMENTS.WINDOW)
        with dpg.window(tag=tag):
            with dpg.group(horizontal=True):
                with dpg.group(width=500):
                    dpg.add_text("Profiles")
                    dpg.add_listbox(
                        [k for k in self.profiles.keys()],
                        tag=self.keys.getKey(Main.ELEMENTS.PROFILES),
                        num_items=30)
                    dpg.add_button(label="Access Profile", tag=self.keys.getKey(Main.ELEMENTS.OPENPROFILE))
                with dpg.group():
                    dpg.add_text("Jobs")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Get All New Jobs", tag=self.keys.getKey(Main.ELEMENTS.OPENPROFILE))
                        dpg.add_button(label="Detail", tag=self.keys.getKey(Main.ELEMENTS.JOBSDETAIL))
                    dpg.add_text("", wrap=100)
        dpg.set_primary_window(tag, True)