import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from dearpygui.dearpygui import *

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=600)

with dpg.window():
    # basic usage of the table api
    with dpg.table(header_row=False):

        # use add_table_column to add columns to the table,
        # table columns use slot 0
        dpg.add_table_column()
        dpg.add_table_column()
        dpg.add_table_column()

        # add_table_next_column will jump to the next row
        # once it reaches the end of the columns
        # table next column use slot 1
        for i in range(4):

            with dpg.table_row():
                for j in range(3):
                    if j == 0:
                        dpg.add_selectable(label=f"Row{i} Column{j}", span_columns=True)
                    else:
                        dpg.add_text(f"Row{i} Column{j}")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()