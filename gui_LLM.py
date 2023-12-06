import gnupg
from pathlib import Path
import json
import gui

def main():
    gpg = gnupg.GPG(gnupghome=Path().home()/'.gnupg')
    LLM_API_Key = None
    with open(Path().home()/'Documents/pwds.txt.gpg', 'rb') as f:
        LLM_API_Key = gpg.decrypt_file(f)
        LLM_API_Key = json.loads(LLM_API_Key.data)['google_bard']
        
    gui.main(LLM_API_Key=LLM_API_Key)


if __name__ == '__main__':
    main()