import PySimpleGUI as sg

sg.theme('DefaultNoMoreNagging')

video_frame_column = [
    [sg.Text("Scanner", justification="center")],
    [sg.Multiline(expand_x=True, expand_y=True, key="-IMAGE-")]
]
functional_column = [
    [sg.Text("Log Settings", justification="center")],
    [
        sg.Text("Scanned ID:", justification="center"),
        sg.Text(size=(30, 1), key="-TOUT-", justification="center", background_color="white")
    ],
    [sg.Button("Enter")],
    [sg.Button("Exit")],
    [sg.Button("Display Log")]
]
layout=[
        [
            sg.Column(video_frame_column, expand_x=True, expand_y=True),
            sg.VSeperator(),
            sg.Column(functional_column, element_justification='c')
        ]
    ]
window = sg.Window("Entry/Exit Log Management System", layout, location=(300, 150), resizable=True, finalize=True)
window.read(close=True)