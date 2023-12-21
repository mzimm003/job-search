import dearpygui.dearpygui as dpg

dpg.create_context()

def call():
    with dpg.window(label="Tutorial2"):
        b0 = dpg.add_button(label="button 3")
        b1 = dpg.add_button(tag=1000, label="Button 4")
        dpg.add_button(tag="Btn5", label="Button 5")    

with dpg.window(label="Tutorial"):
    with dpg.group(horizontal=True):
        with dpg.group():
            with dpg.group(horizontal=True):
                b0 = dpg.add_button(label="button 0")
                b1 = dpg.add_button(tag=1001, label="Button 1", callback=call)
                dpg.add_button(tag="Btn2.1", label="Button 2")
            with dpg.group(horizontal=True):
                b0 = dpg.add_button(label="button 0")
                b1 = dpg.add_button(tag=100, label="Button 1", callback=call)
                dpg.add_button(tag="Btn2", label="Button 2")
        with dpg.group():
            with dpg.group(horizontal=True):
                b0 = dpg.add_button(label="button 0")
                b1 = dpg.add_button(tag=10011, label="Button 1", callback=call)
                dpg.add_button(tag="Btn2.11", label="Button 2")
            with dpg.group(horizontal=True):
                b0 = dpg.add_button(label="button 0")
                b1 = dpg.add_button(tag=1001, label="Button 1", callback=call)
                dpg.add_button(tag="Btn21", label="Button 2")

dpg.create_viewport(title='Custom Title', width=600, height=200)
dpg.show_viewport()
dpg.create_viewport(title='Second Title', width=600, height=200)
dpg.show_viewport()
dpg.setup_dearpygui()
dpg.start_dearpygui()
dpg.destroy_context()
