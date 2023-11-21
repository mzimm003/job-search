import PySimpleGUI as sg
from Search.transforms import Transform
from Search.profile import Profile
from Search.search import Search
import pickle
from pathlib import Path
from typing import (
    Dict
)

def errorMsg(message, window):
    lyt = [
        [sg.Text(message)],
        [sg.Button("OK")]
        ]
    w = sg.Window("Error", lyt, modal=True, location=window.current_location())
    while True:
        e, v = w.read()
        if e == "OK" or e == sg.WIN_CLOSED:
            break
    w.close()

def profileWindow(window, profileStr:str, profile:Profile):
    lyt = [
        []
    ]
    w = sg.Window(profileStr, lyt, location=window.current_location())


def main():
    profiles:Dict[str, Profile] = {}
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            profiles = pickle.load(f)

    search_panel_layout = [
        [sg.Text("Search Parameters")],
        [sg.Text("Header")],
        [sg.Multiline(enable_events=True, key="SEARCH", expand_x=True, expand_y=True)],
        [sg.Text("Job Identifying Keyword")],
        [sg.In(size=(20, 1), enable_events=True, key="KEYID", expand_x=True)],
        [sg.Button("Add Search"), sg.Button("Create Profile from Search")]
    ]
    layout_l = search_panel_layout

    layout_r = [
        [sg.Listbox([k for k in profiles.keys()], no_scrollbar=True, expand_x=True, expand_y=True, key="PROFILES")],
        [sg.Button("View Profile")]
        ]

    layout = [
        [
            sg.Col(layout_l, expand_x=True, expand_y=True),
            sg.Col(layout_r, expand_x=True, expand_y=True)
        ]
    ]

    # Create the window
    window = sg.Window("Work", layout, enable_close_attempted_event=True, resizable=True)

    # Create an event loop
    while True:
        event, values = window.read()
        if event == "Add Search" or event == "Create Profile from Search":
            if values['SEARCH'] == '' or values['KEYID'] == '':
                errorMsg("Must fill the search parameters, 'Header' and 'Job Indetifying Keyword'", window)
            else:
                search_header = Transform().GUIRequestHeaderToRequestParamDict(values['SEARCH'])
                search = Search.byHTML(searchReq=search_header, jobKeyId=values['KEYID'])
                if event == "Add Search":
                    for p in values['PROFILES']:
                        profiles[p].addSearch(search)
                else:
                    name = search_header['url'].lstrip('https://')
                    name = name[:name.find('/')]
                    profiles[name] = Profile(name)
                    profiles[name].addSearch(search)
                    window['PROFILES'].update([k for k in profiles.keys()])
            
        if event == "View Profile":
            for p in values['PROFILES']:
                profileWindow(window, p)

        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == sg.WIN_CLOSED or event == sg.WIN_X_EVENT:
            lyt = [
                [sg.Text('Save Work?')],
                [sg.Button("Yes"),sg.Button("No")]
                ]
            save_window = sg.Window("Save?", lyt, modal=True, location=window.current_location())
            while True:
                e, v = save_window.read()
                if e == "Yes":
                    with open("Search/profiles.pkl", "wb") as f:
                        pickle.dump(profiles, f)
                    break
                if e == "No" or e == sg.WIN_CLOSED:
                    break
            save_window.close()
            break

    window.close()

if __name__ == "__main__":
    main()