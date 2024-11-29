from jobsearch.backend.backend import Backend
from jobsearch.gui.module import Module
import dearpygui.dearpygui as dpg
import enum


class Menu(Module):
    class ELEMENTS(enum.Enum):
        LLM_OPTIONS = enum.auto()
        LLM_OPTIONS_HANDLER = enum.auto()
    def __init__(self, backend: Backend) -> None:
        super().__init__(backend)

    def newWindow(self):
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save", callback=self.backend.save_portfolio)

            with dpg.menu(label="LLM"):
                dpg.add_menu_item(label="Add LLM", callback=self.add_llm) #TODO, create callback
                dpg.add_menu(label="Switch", tag=self.getKey(Menu.ELEMENTS.LLM_OPTIONS))
                self.refresh_llm_options()
                self.select_llm_by_name(self.backend.get_default_llm_model_name())
                dpg.add_menu_item(label="Settings", callback=self.llm_settings)

            dpg.add_menu_item(label="Help") #TODO, create callback

    def refresh_llm_options(self):
        dpg.delete_item(self.getKey(Menu.ELEMENTS.LLM_OPTIONS), children_only=True)
        for llm in self.backend.get_llm_model_option_names():
            dpg.add_menu_item(
                label=llm,
                callback=self.choose_llm,
                check=True,
                parent=self.getKey(Menu.ELEMENTS.LLM_OPTIONS))

    def check_as_radio(self, sender, app_data, user_data):
        sibling_options = dpg.get_item_children(dpg.get_item_parent(sender),1)
        for sib in sibling_options:
            dpg.set_value(sib, False)
        dpg.set_value(sender, True)
    
    def add_llm(self, sender, app_data, user_data):
        newllm = AddLLM(backend=self.backend, menu=self)
        newllm.newWindow()

    def choose_llm(self, sender, app_data, user_data):
        self.check_as_radio(sender, app_data, user_data)
        self.backend.set_llm_model(dpg.get_item_label(sender))
    
    def select_llm_by_name(self, name):
        if name:
            selections = dpg.get_item_children(self.getKey(Menu.ELEMENTS.LLM_OPTIONS), 1)
            new_select = None
            for s in selections:
                if dpg.get_item_label(s) == name:
                    new_select = s
            self.choose_llm(new_select,None,None)
    
    def llm_settings(self, sender, app_data, user_data):
        sett = LLMOptions(backend=self.backend, menu=self)
        sett.newWindow()

class LLMOptions(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        SELECTION = enum.auto()
        OPTION = enum.auto()

    def __init__(self, backend: Backend, menu:Menu) -> None:
        super().__init__(backend)
        self.menu = menu
        self.options_mapping = {}
        self.api_key_hidden = True

    def newWindow(self):
        tag = self.getKey(LLMOptions.ELEMENTS.WINDOW)
        with dpg.window(
            label="LLM Settings",
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            tag=tag,
            width=800):
            with dpg.group(horizontal=True):
                dpg.add_listbox(
                    self.backend.get_llm_model_option_names(),
                    tag=self.getKey(LLMOptions.ELEMENTS.SELECTION),
                    num_items=25,
                    width=300,
                    callback=self.add_options,
                    default_value=self.backend.get_default_llm_model_name())
                with dpg.group():
                    dpg.add_child_window(
                        tag=self.getKey(LLMOptions.ELEMENTS.OPTION),
                        height=dpg.get_item_height(self.getKey(LLMOptions.ELEMENTS.SELECTION))-50)
                    self.add_options()
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Save Changes",
                            callback=self.update_options)
                        dpg.add_spacer(width=275)
                        dpg.add_button(
                            label="DELETE MODEL",
                            callback=self.delete_model)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="OK",
                    callback=self.ok)
                dpg.add_button(
                    label="Cancel",
                    callback=self.cancel)

    def add_options(self):
        model = dpg.get_value(self.getKey(LLMOptions.ELEMENTS.SELECTION))
        dpg.delete_item(self.getKey(LLMOptions.ELEMENTS.OPTION), children_only=True)
        for k,v in self.backend.get_model_options_by_name(name=model).items():
            tag = self.getKey(LLMOptions.ELEMENTS.OPTION, withCount=True)
            self.options_mapping[k] = tag
            if type(v) in [int, float]:
                dpg.add_input_text(
                    default_value=str(v),
                    label=k,
                    decimal=True,
                    tag=tag,
                    parent=self.getKey(LLMOptions.ELEMENTS.OPTION))
            elif type(v) in [str]:
                dpg.add_input_text(
                    default_value=v,
                    label=k,
                    tag=tag,
                    parent=self.getKey(LLMOptions.ELEMENTS.OPTION))

    def update_options(self):
        model = dpg.get_value(self.getKey(LLMOptions.ELEMENTS.SELECTION))
        options = {}
        for o,key in self.options_mapping.items():
            options[o] = dpg.get_value(key)
        self.backend.set_model_options_by_name(
            name=model,
            options=options)

    def refresh_llm_model_list(self):
        dpg.configure_item(
            self.getKey(LLMOptions.ELEMENTS.SELECTION),
            items=self.backend.get_llm_model_option_names())

    def delete_model(self):
        model = dpg.get_value(self.getKey(LLMOptions.ELEMENTS.SELECTION))
        self.backend.delete_llm_model(model)
        self.refresh_llm_model_list()
        self.menu.refresh_llm_options()

    def ok(self):
        self.update_options()
        self.menu.refresh_llm_options()
        dpg.delete_item(self.getKey(AddLLM.ELEMENTS.WINDOW))
    
    def cancel(self):
        dpg.delete_item(self.getKey(AddLLM.ELEMENTS.WINDOW))


class AddLLM(Module):
    class ELEMENTS(enum.Enum):
        WINDOW = enum.auto()
        API_OPTION = enum.auto()
        API_CHOICE = enum.auto()
        API_KEY = enum.auto()
        SHOWBUTTON = enum.auto()
        NAME = enum.auto()
        OPTION = enum.auto()
        OK = enum.auto()
        CANCEL = enum.auto()
    def __init__(self, backend: Backend, menu:Menu) -> None:
        super().__init__(backend)
        self.menu = menu
        self.options_mapping = {}
        self.api_key_hidden = True

    def newWindow(self):
        tag = self.getKey(AddLLM.ELEMENTS.WINDOW)
        with dpg.window(
            label="Add LLM Model Configuration",
            pos=self.proposePosition(),
            on_close=self.cleanAliases,
            tag=tag,
            width=500):
            dpg.add_text("API Type")
            default_api = self.backend.get_llm_api_options()[0]
            dpg.add_radio_button(
                self.backend.get_llm_api_options(),
                tag=self.getKey(AddLLM.ELEMENTS.API_CHOICE),
                default_value=default_api,
                callback=self.add_options)
            with dpg.group(
                tag=self.getKey(AddLLM.ELEMENTS.API_OPTION),
                show=not self.backend.api_key_exists(default_api)):
                self.add_password_module()
            dpg.add_separator()
            dpg.add_input_text(label="Name", tag=self.getKey(AddLLM.ELEMENTS.NAME))
            with dpg.group(tag=self.getKey(AddLLM.ELEMENTS.OPTION)):
                self.add_options()
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="OK",
                    tag=self.getKey(AddLLM.ELEMENTS.OK),
                    callback=self.ok)
                dpg.add_button(
                    label="Cancel",
                    tag=self.getKey(AddLLM.ELEMENTS.CANCEL),
                    callback=self.cancel)

    def add_options(self):
        api = dpg.get_value(self.getKey(AddLLM.ELEMENTS.API_CHOICE))
        if not self.backend.api_key_exists(api):
            dpg.show_item(self.getKey(AddLLM.ELEMENTS.API_OPTION))
        else:
            dpg.hide_item(self.getKey(AddLLM.ELEMENTS.API_OPTION))
        dpg.delete_item(self.getKey(AddLLM.ELEMENTS.OPTION), children_only=True)
        for k,v in self.backend.get_default_options(api=api).items():
            tag = self.getKey(AddLLM.ELEMENTS.OPTION, withCount=True)
            self.options_mapping[k] = tag
            if type(v) in [int, float]:
                dpg.add_input_text(
                    default_value=str(v),
                    label=k,
                    decimal=True,
                    tag=tag,
                    parent=self.getKey(AddLLM.ELEMENTS.OPTION))
            elif type(v) in [str]:
                dpg.add_input_text(
                    default_value=v,
                    label=k,
                    tag=tag,
                    parent=self.getKey(AddLLM.ELEMENTS.OPTION))

    def add_password_module(self, label="API Key", **kwargs):
        hidden_api_tag = self.getKey(AddLLM.ELEMENTS.API_KEY, withCount=True)
        shown_api_tag = self.getKey(AddLLM.ELEMENTS.API_KEY, withCount=True)

        def showhide():
            if self.api_key_hidden:
                dpg.set_item_label(self.getKey(AddLLM.ELEMENTS.SHOWBUTTON), "Hide")
                dpg.hide_item(hidden_api_tag)
                dpg.show_item(shown_api_tag)
                self.api_key_hidden = False
            else:
                dpg.set_item_label(self.getKey(AddLLM.ELEMENTS.SHOWBUTTON), "Show")
                dpg.hide_item(shown_api_tag)
                dpg.show_item(hidden_api_tag)
                self.api_key_hidden = True
        with dpg.group(horizontal=True):
            password = dpg.add_input_text(
                label=label,
                password=True,
                tag=hidden_api_tag,
                **kwargs)
            dpg.add_input_text(
                label=label,
                source=password,
                show=False,
                tag=shown_api_tag,
                **kwargs)
            dpg.add_button(
                label="Show",
                tag=self.getKey(AddLLM.ELEMENTS.SHOWBUTTON),
                callback=showhide)

    def ok(self):
        api = dpg.get_value(self.getKey(AddLLM.ELEMENTS.API_CHOICE))
        api_key = dpg.get_value(
            self.keys.getKeyAppendingCount(AddLLM.ELEMENTS.API_KEY, 0))
        model_name = dpg.get_value(self.getKey(AddLLM.ELEMENTS.NAME))
        options = {}
        for o,key in self.options_mapping.items():
            options[o] = dpg.get_value(key)
        self.backend.add_llm_model(
            api=api,
            api_key=api_key,
            model_name=model_name,
            model_options=options)
        self.menu.refresh_llm_options()
        self.menu.select_llm_by_name(model_name)
        dpg.delete_item(self.getKey(AddLLM.ELEMENTS.WINDOW))
    
    def cancel(self):
        dpg.delete_item(self.getKey(AddLLM.ELEMENTS.WINDOW))