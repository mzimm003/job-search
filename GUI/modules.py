import abc
import enum

class Module(abc.ABC):
    @abc.abstractmethod
    def newWindow(self):
        pass

class Main(Module):
    class ELEMENTS(enum.Enum):
        PROFILES = enum.auto()
        JOBSDETAIL = enum.auto()
        ALLNEWJOBS = enum.auto()
        NEWJOBS = enum.auto()
        OPENPROFILE = enum.auto()

    def newWindow(self):
        return super().newWindow()