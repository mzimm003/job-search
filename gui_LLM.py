import gnupg
from pathlib import Path
import json
import gui
import platform

def main():
    gpgDict = {"gnupghome": Path().home()/'.gnupg'}
    if platform.system() == 'Windows':
        gpgDict['gnupghome'] = Path().home()/'AppData'/'Roaming'/'gnupg'
        gpgDict['gpgbinary'] = Path("C:/Program Files (x86)/gnupg/bin/gpg.exe")
    gpg = gnupg.GPG(**gpgDict)
    LLM_API_Key = None
    with open(Path().home()/'Documents/pwds.txt.gpg', 'rb') as f:
        LLM_API_Key = gpg.decrypt_file(f)
        LLM_API_Key = json.loads(LLM_API_Key.data)['google_bard']
        
    gui.main(LLM_API_Key=LLM_API_Key)

if __name__ == '__main__':
    main()