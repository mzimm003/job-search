import dearpygui.dearpygui as dpg
from pathlib import Path
import pickle
from Search.profile import (
    Profile,
    Portfolio
)
from GUI.modules import (
    Main
)
from Resumes.llm import LLM

class GUI:
    def __init__(
            self,
            portfolio:Portfolio=None,
            llm:LLM=None,
            ) -> None:
        self.portfolio = portfolio
        self.llm = llm
        self.primaryWindow = Main(self.portfolio.getProfiles())
        dpg.create_context()
        dpg.create_viewport(title='Custom Title', width=600, height=200, disable_close=True)
        dpg.set_exit_callback(self.endProgram)

    def run(self):
        self.primaryWindow.newWindow()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
    
    def endProgram(self, sender, app_data, user_data):
        def Yes(sender, app_data, user_data):
            with open("Search/profiles.pkl", "wb") as f:
                pickle.dump(self.portfolio, f)
            dpg.destroy_context()
        def No(sender, app_data, user_data):
            dpg.destroy_context()

        with dpg.window():
            dpg.add_text("Save Work?")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", callback=Yes)
                dpg.add_button(label="No", callback=No)

def main(LLM_API_Key=''):
    # port:Portfolio = Portfolio()
    # port.addProfile(Profile(GUI.NEWPROFILE))
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            port = pickle.load(f)
    llm = None
    if LLM_API_Key:
        llm = LLM(LLM_API_Key)
    gui = GUI(portfolio=port, llm=llm)

    gui.run()

if __name__ == "__main__":
    main()