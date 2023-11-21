import PySimpleGUI as sg
from Search.transforms import Transform
from Search.profile import Profile
from Search.search import Search
import pickle
from pathlib import Path

def main():
    profiles = {}
    if Path('Search/profiles.pkl').exists():
        with open('Search/profiles.pkl', 'rb') as f:
            profiles = pickle.load(f)

    layout_l = [
        [
            sg.Text("Image Folder"),
            sg.Multiline(size=(40, 40), enable_events=True, key="SEARCH"),
        ],
        [sg.In(size=(40, 1), enable_events=True, key="KEYID")],
        [sg.Button("Add Search"), sg.Button("Create Profile from Search")],
        [sg.Button("OK")]
        ]

    layout_r = [
        [sg.Listbox([k for k in profiles.keys()], no_scrollbar=True,  s=(15,2), key="PROFILES")],
        ]

    layout = [
        [sg.Col(layout_l), sg.Col(layout_r)]
    ]

    # Create the window
    window = sg.Window("Work", layout, enable_close_attempted_event=True)

    # Create an event loop
    while True:
        event, values = window.read()
        if event == "Add Search" or event == "Create Profile from Search":
            if values['SEARCH'] == '' or values['KEYID'] == '':
                lyt = [
                    [sg.Text('Must fill Search Headers and Job Key ID')],
                    [sg.Button("OK")]
                    ]
                w = sg.Window("Error", lyt, modal=True, location=window.current_location())
                while True:
                    e, v = w.read()
                    if e == "OK" or e == sg.WIN_CLOSED:
                        break
                w.close()
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