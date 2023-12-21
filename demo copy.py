import dearpygui.dearpygui as dpg
import argparse
import enum

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action='store_true')
args = parser.parse_args()

class RESUMEELEMENTS(enum.Enum):
    EXPERIENCE = enum.auto()
    EXPKEEP = enum.auto()
    EXPREVISION = enum.auto()
    SKILL = enum.auto()
    SKLKEEP = enum.auto()
    SKLREVISION = enum.auto()
    AIEXP = enum.auto()
    AISKILL = enum.auto()
    RUNAI = enum.auto()
    SAVEJSON = enum.auto()
    SAVEPDF = enum.auto()
    BACK = enum.auto()
    NEXT = enum.auto()
class KeyCount:
    def __init__(self) -> None:
        self.counts = {k:0 for k in RESUMEELEMENTS}
    def getKey(self, k):
        ret = self.counts[k]
        self.counts[k] += 1
        return str((k, ret))

keys = KeyCount()

# Callback function for the "OK" button to close the window
def close_window(sender, app_data):
    dpg.delete_item(dpg.get_item_parent(sender))

def save(sender, app_data):
    with dpg.window(tag=keys.getKey(RESUMEELEMENTS.EXPERIENCE), label="SAVE?", width=300, height=200):
        dpg.add_text("This is the second window")
        dpg.add_button(tag=keys.getKey(RESUMEELEMENTS.EXPERIENCE), label="OK", callback=lambda x:dpg.destroy_context())


# Callback function for the first button to open the second window
def open_second_window(sender, app_data):
    with dpg.window(tag=keys.getKey(RESUMEELEMENTS.EXPERIENCE), label="Second Window", width=300, height=200):
        dpg.add_text("This is the second window")
        dpg.add_button(tag=keys.getKey(RESUMEELEMENTS.EXPERIENCE), label="OK", callback=close_window)

# Main code
dpg.create_context()
if args.debug:
    dpg.configure_app(manual_callback_management=True)
dpg.create_viewport(disable_close=True)
dpg.set_exit_callback(save)
dpg.show_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Main Window"):
    dpg.add_text("Click the button to open the second window:")
    dpg.add_button(label="Open Second Window", callback=open_second_window)

if args.debug:
    while dpg.is_dearpygui_running():
        jobs = dpg.get_callback_queue() # retrieves and clears queue
        dpg.run_callbacks(jobs)
        dpg.render_dearpygui_frame()
else:
    dpg.start_dearpygui()

dpg.destroy_context()


# import dearpygui.dearpygui as dpg

# dpg.create_context()

# def call():
#     with dpg.window(label="Tutorial2"):
#         b0 = dpg.add_button(label="button 3")
#         b1 = dpg.add_button(tag=1000, label="Button 4")
#         dpg.add_button(tag="Btn5", label="Button 5")    

# with dpg.window(label="Tutorial"):
#     with dpg.group(horizontal=True):
#         with dpg.group():
#             with dpg.group(horizontal=True):
#                 b0 = dpg.add_button(label="button 0")
#                 b1 = dpg.add_button(tag=1001, label="Button 1", callback=call)
#                 dpg.add_button(tag="Btn2.1", label="Button 2")
#             with dpg.group(horizontal=True):
#                 b0 = dpg.add_button(label="button 0")
#                 b1 = dpg.add_button(tag=100, label="Button 1", callback=call)
#                 dpg.add_button(tag="Btn2", label="Button 2")
#         with dpg.group():
#             with dpg.group(horizontal=True):
#                 b0 = dpg.add_button(label="button 0")
#                 b1 = dpg.add_button(tag=10011, label="Button 1", callback=call)
#                 dpg.add_button(tag="Btn2.11", label="Button 2")
#             with dpg.group(horizontal=True):
#                 b0 = dpg.add_button(label="button 0")
#                 b1 = dpg.add_button(tag=1001, label="Button 1", callback=call)
#                 dpg.add_button(tag="Btn21", label="Button 2")

# dpg.create_viewport(title='Second Title', width=600, height=200)
# dpg.show_viewport()
# dpg.setup_dearpygui()
# dpg.start_dearpygui()
# dpg.destroy_context()
