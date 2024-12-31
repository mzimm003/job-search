from jobsearch.gui.module import Module
from jobsearch.backend.userprofile import (
    NestingDataClass,
    DataClass,
    UserProfile
)
import enum
import dearpygui.dearpygui as dpg
import types
import datetime
import dataclasses

class Element:
    _registry:dict[type, 'Element'] = {}

    @classmethod
    def register_element(cls, input_type: type):
        def decorator(subclass: type[Element]):
            cls._registry[input_type] = subclass
            return subclass
        return decorator
    
    @classmethod
    def type_is_registered(cls, typ:type):
        return typ in cls._registry

    @classmethod
    def add(
            cls,
            default_value,
            label="",
            **kwargs)->'Element':
        """
        Add DearPyGUI element.

        Args:
            default_value: Value with which to fill element.
            label: Element designation.
            kwargs: Additional key word arguments to be passed to DPG element.
        """
        subclass = cls._registry.get(type(default_value))
        if subclass is None:
            raise ValueError(f"No registered subclass for type {type(default_value)}")
        return subclass(
            default_value=default_value,
            label=label,
            **kwargs
        )

    def __init__(
            self,
            dpg_method:types.FunctionType,
            default_value,
            label="",
            **kwargs,
            ):
        self.dpg_method = dpg_method
        self.label = label
        self.dpg_id_num = self.dpg_method(
            label=label,
            default_value=default_value,
            **kwargs)

    def configure(self, **kwargs):
        dpg.configure_item(self.dpg_id_num, **kwargs)

    def get_tag(self):
        return self.dpg_id_num
    
    def get_value(self):
        return dpg.get_value(self.dpg_id_num)

@Element.register_element(int)
class IntElement(Element):
    def __init__(
            self,
            default_value:int,
            label:str="",
            **kwargs
            ):
        super().__init__(
            dpg_method=dpg.add_input_int,
            default_value=default_value,
            label=label,
            step=1
            **kwargs,
        )

@Element.register_element(str)
class StrElement(Element):
    def __init__(
            self,
            default_value:str,
            label:str="",
            **kwargs
            ):
        if label == "Summary":
            kwargs['multiline']=True
            kwargs['height']=250
        if label == "" and not 'width' in kwargs:
            kwargs['width']=-10
        super().__init__(
            dpg_method=dpg.add_input_text,
            default_value=default_value,
            label=label,
            **kwargs,
        )

@Element.register_element(float)
class FloatElement(Element):
    def __init__(
            self,
            default_value:float,
            label:str="",
            **kwargs
            ):
        super().__init__(
            dpg_method=dpg.add_input_float,
            default_value=default_value,
            label=label,
            **kwargs,
        )

@Element.register_element(datetime.date)
class DateElement(Element):
    def __init__(
            self,
            default_value:datetime.date,
            label:str="",
            **kwargs
            ):
        super().__init__(
            dpg_method=dpg.add_input_intx,
            default_value=[default_value.year, default_value.month],
            label=label,
            size=2,
            **kwargs,
        )

    def get_value(self):
        value = super().get_value()
        return datetime.date(*value[:2],1)

class ElementCollection:
    def __init__(
            self,
            user_profile_section:DataClass|list,
            parent:int
            ):
        self.user_profile_section = user_profile_section
        self.parent = parent
        self.element_mapping = {}
        self.is_list = isinstance(self.user_profile_section, list)
    
    def get_values(self):
        d = {}
        for k, v in self.element_mapping.items():
            if isinstance(v, ElementCollection):
                d[k] = v.get_values()
            elif isinstance(v, Element):
                d[k] = v.get_value()
        if self.is_list:
            d = list(d.values())
        return d
    
    def add_element(
            self,
            user_profile_element,
            default_value,
            parent,
            label="",
            **kwargs,):
        element = Element.add(
            default_value=default_value,
            label=label,
            parent=parent,
            **kwargs
        )
        self.element_mapping[user_profile_element] = element

    def add_collection(
            self,
            user_profile_element,
            data,
            parent,
            label="",):
        sub_parent = dpg.add_child_window(auto_resize_y=True, parent=parent)
        dpg.add_text(label, parent=sub_parent)
        collection = ElementCollection(
            user_profile_section=data,
            parent=sub_parent
        )
        collection.map_fields()
        if collection.is_list:
            dpg.add_button(
                label="+",
                callback=self.append_element,
                user_data=dict(
                    collection=collection,
                    collection_name=user_profile_element),
                parent=sub_parent)
        self.element_mapping[user_profile_element] = collection

    def append_element(self, sender, app_data, user_data):
        collection:ElementCollection = user_data['collection']
        collection_name:str = user_data['collection_name']
        self.user_profile_section.add_new_list_item(collection_name)
        collection_data = self.user_profile_section.get(collection_name)
        new_elem = collection_data[-1]
        collection.map_removeable_field(
            typ=type(new_elem),
            name=len(collection_data),
            data=new_elem,
            parent=collection.parent
        )
        dpg.move_item_down(sender)

    def remove_element(self, sender, app_data, user_data):
        parent = user_data['parent']
        field_name = user_data['name']
        # self.user_profile_section.add_new_list_item(collection_name)
        del self.element_mapping[field_name]
        dpg.delete_item(parent)
        
    def map_field(
            self,
            typ:type,
            name:str,
            data,
            parent,
            label:str="",
            **kwargs,
            ):
            if Element.type_is_registered(typ=typ):
                self.add_element(
                    user_profile_element=name,
                    default_value=data,
                    label=label,
                    parent=parent,
                    **kwargs)
            else:
                self.add_collection(
                    user_profile_element=name,
                    data=data,
                    label=label,
                    parent=parent)

    def map_removeable_field(
            self,
            typ:type,
            name:str,
            data,
            parent,
            label:str="",
            **kwargs,
            ):
        sub_parent = dpg.add_group(horizontal=True, parent=parent)
        dpg.add_button(
            label="-",
            parent=sub_parent,
            callback=self.remove_element,
            user_data=dict(parent=sub_parent,
                           name=name))
        self.map_field(
            typ=typ,
            name=name,
            data=data,
            parent=sub_parent,
            label=label,
            **kwargs,)

    def map_fields(self):
        if dataclasses.is_dataclass(self.user_profile_section):
            for field in self.user_profile_section.fields():
                label = self.label_from_user_profile_element(field.name)
                data = self.user_profile_section.get(field.name)
                self.map_field(
                    typ=field.type,
                    name=field.name,
                    data=data,
                    label=label,
                    parent=self.parent
                )
        elif isinstance(self.user_profile_section, list):
            for i, field in enumerate(self.user_profile_section):
                self.map_removeable_field(
                    typ=type(field),
                    name=i,
                    data=field,
                    parent=self.parent
                )

    def label_from_user_profile_element(self, user_profile_element:str):
        return user_profile_element.capitalize().replace("_"," ")

class GUIUserProfileUpdateModule(Module):
    class ELEMENTS(enum.Enum):
        HANDLER_REG = enum.auto()
        TAB = enum.auto()
        INPUTS = enum.auto()

    def __init__(
            self,
            backend,
            user_profile_section:NestingDataClass,
            user_profile:'GUIUserProfile'
            ) -> None:
        super().__init__(backend=backend)
        self.user_profile_section = user_profile_section
        self.user_profile = user_profile
        self.data:ElementCollection = None

    def activate_tab(self):
        self.user_profile.activate_tab(self)
    
    def set_tab(self):
        self.user_profile_section.set(
            self.as_dict()
        )

    def as_dict(self):
        return self.data.get_values()
    
    def newWindow(self, label="", **kwargs):
        self.tab = self.newTab(label=label, **kwargs)
        self.set_data(user_profile_section=self.user_profile_section)
    
    def set_data(self, user_profile_section):
        self.user_profile_section = user_profile_section
        self.data = ElementCollection(
            user_profile_section=self.user_profile_section,
            parent=self.tab
        )
        self.data.map_fields()

    def newTab(self, label, **kwargs):
        tab = dpg.add_tab(
            label=label,
            tag=self.getKey(GUIUserProfileUpdateModule.ELEMENTS.TAB),
            **kwargs)
            
        with dpg.item_handler_registry(
            tag=self.getKey(GUIUserProfileUpdateModule.ELEMENTS.HANDLER_REG)):
            
            dpg.add_item_activated_handler(
                callback=self.activate_tab,
                user_data=self.getKey(GUIUserProfileUpdateModule.ELEMENTS.TAB))
        
        dpg.bind_item_handler_registry(
            self.getKey(GUIUserProfileUpdateModule.ELEMENTS.TAB),
            self.getKey(GUIUserProfileUpdateModule.ELEMENTS.HANDLER_REG))
        return tab

class GUIBasicInfo(GUIUserProfileUpdateModule):
    def newWindow(self, **kwargs):
        super().newWindow(
            label="Basic Information",
            **kwargs)
        # with dpg.theme() as global_theme:
        #     with dpg.theme_component(dpg.mvInputText):
        #         dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (140, 255, 23), category=dpg.mvThemeCat_Core)
        #         dpg.add_theme_style(dpg.mvStyleVar_FrameWidth, 5, category=dpg.mvThemeCat_Core)

        # dpg.bind_item_theme(self.tab, global_theme)

class GUIWorkExperiences(GUIUserProfileUpdateModule):
    def newWindow(self, **kwargs):
        super().newWindow(
            label="Work Experience",
            **kwargs)
        
class GUIProjects(GUIUserProfileUpdateModule):
    def newWindow(self, **kwargs):
        super().newWindow(
            label="Projects",
            **kwargs)
        
class GUIEducation(GUIUserProfileUpdateModule):
    def newWindow(self, **kwargs):
        super().newWindow(
            label="Education",
            **kwargs)
        
class GUISkills(GUIUserProfileUpdateModule):
    def newWindow(self, **kwargs):
        super().newWindow(
            label="Skills",
            **kwargs)

class GUIUserProfile(Module):
    class ELEMENTS(enum.Enum):
        TABS = enum.auto()
    
    def __init__(
            self,
            backend
            ) -> None:
        super().__init__(backend=backend)
        self.tabs:dict[str,GUIUserProfileUpdateModule] = {}
        self.active_tab:GUIUserProfileUpdateModule = None
        self.user_profile_copy:UserProfile = self.backend.get_user_profile().copy()
    
    def add_tab(
            self,
            user_profile_section,
            tab:type[GUIUserProfileUpdateModule],
            **kwargs):
        tab = tab(
            backend=self.backend,
            user_profile_section=getattr(
                self.user_profile_copy,
                user_profile_section),
            user_profile=self
            )
        tab.newWindow(**kwargs)
        self.tabs[user_profile_section] = tab
        return tab
    
    def set_active_tab(self):
        self.active_tab.set_tab()
    
    def activate_tab(self, tab):
        if self.active_tab:
            self.set_active_tab()
        self.active_tab = tab

    def commit_changes(self):
        self.set_active_tab()
        self.backend.get_user_profile().set(
            self.user_profile_copy.as_dict())

    def revert_changes(self):
        self.user_profile_copy:UserProfile = self.backend.get_user_profile().copy()
        for user_profile_section, tab in self.tabs.items():
            dpg.delete_item(
                tab.tab,
                children_only=True)
            user_profile_section = getattr(
                self.user_profile_copy,
                user_profile_section)
            tab.set_data(user_profile_section=user_profile_section)

    def create_tabs(self, parent=None):
        add_kwargs = dict()
        if parent:
            add_kwargs['parent'] = parent
        profile = self.user_profile_copy
        first_tab = self.add_tab(
            user_profile_section="basic_info",
            tab=GUIBasicInfo,
            **add_kwargs
            )
        first_tab.activate_tab()
        self.add_tab(
            user_profile_section="work_experience",
            tab=GUIWorkExperiences,
            **add_kwargs
            )
        self.add_tab(
            user_profile_section="projects",
            tab=GUIProjects,
            **add_kwargs
            )
        self.add_tab(
            user_profile_section="education",
            tab=GUIEducation,
            **add_kwargs
            )
        self.add_tab(
            user_profile_section="skills",
            tab=GUISkills,
            **add_kwargs
            )

    def newWindow(self):
        with dpg.tab(label="User Profile"):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Commit Changes", callback=self.commit_changes)
                dpg.add_button(label="Revert Changes", callback=self.revert_changes)
            with dpg.tab_bar(tag=self.getKey(GUIUserProfile.ELEMENTS.TABS)):
                self.create_tabs()