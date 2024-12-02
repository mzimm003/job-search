import dearpygui.dearpygui as dpg

from jobsearch.backend.backend import Backend
from jobsearch.gui.modules import GUIMain, GUISignIn
from jobsearch.search.utility import errorWindow

import traceback

class GUI:
    def __init__(
            self,
            backend:Backend,
            debug:bool=False,
            ) -> None:
        self.backend = backend
        self.debug = debug
        self.primaryWindow = GUIMain(backend=self.backend)
        self.sign_in = GUISignIn(
            backend=self.backend,
            primary_window=self.primaryWindow)
        dpg.create_context()
        # if self.debug:
        #     dpg.configure_app(manual_callback_management=True) #Cannot get non-manual callback to work with html_requests render
        dpg.configure_app(manual_callback_management=True)
        dpg.create_viewport(title='Custom Title', width=600, height=200, disable_close=True)
        dpg.set_exit_callback(self.endProgram)

    def run(self):
        self.sign_in.newWindow()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.maximize_viewport()

        # if self.debug:
        #     while dpg.is_dearpygui_running():
        #         jobs = dpg.get_callback_queue() # retrieves and clears queue
        #         dpg.run_callbacks(jobs)
        #         dpg.render_dearpygui_frame()
        # else:
        #     dpg.start_dearpygui() #Cannot get to work with html_requests render
        while dpg.is_dearpygui_running():
            try:
                jobs = dpg.get_callback_queue() # retrieves and clears queue
                dpg.run_callbacks(jobs)
            except Exception as inst:
                errorWindow("Something went wrong.\n{}:{}\n{}".format(type(inst), inst, traceback.format_exc()))
            finally:
                dpg.render_dearpygui_frame()

        dpg.destroy_context()
    
    def endProgram(self, sender, app_data, user_data):
        def Yes(sender, app_data, user_data):
            self.backend.save_portfolio()
            dpg.destroy_context()
        def No(sender, app_data, user_data):
            dpg.destroy_context()

        with dpg.window(pos=(dpg.get_viewport_width()//2, dpg.get_viewport_height()//2)):
            dpg.add_text("Save Work?")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", callback=Yes)
                dpg.add_button(label="No", callback=No)