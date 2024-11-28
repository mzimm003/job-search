from jobsearch.backend.backend import Backend

import abc
import dearpygui.dearpygui as dpg


class Module(abc.ABC):
    def __init__(self, backend:Backend) -> None:
        super().__init__()
        self.keys = Keys(self.__class__)
        self.aliasesCreated = []
        self.backend = backend
    @abc.abstractmethod
    def newWindow(self):
        ...
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