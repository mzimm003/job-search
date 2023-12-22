import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Width-Limited Group Example"):
    # Create a parent group with a specific width
    with dpg.group(width=300):  # Adjust width as needed
        dpg.add_text("Parent Group with Limited Width")
        
        # Create a child group (acting as a column) with horizontal layout
        with dpg.group(horizontal=True):
            # Set a specific width for the child group
            with dpg.group(width=200):  # Adjust width as needed
                dpg.add_text("Widget 1")
                dpg.add_button(label="Button 1")
                dpg.add_input_text(label="Input 1")

            # Add a separator between the groups
            dpg.add_separator()

            # Another child group with horizontal layout
            with dpg.group(horizontal=True):
                dpg.add_text("Widget 2")
                dpg.add_button(label="Button 2")
                dpg.add_input_text(label="Input 2")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
