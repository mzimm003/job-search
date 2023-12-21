import dearpygui.dearpygui as dpg

class GUI:
    def __init__(
            self
            ) -> None:
        dpg.create_context()
        dpg.create_viewport(title='Custom Title', width=600, height=200)

    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
