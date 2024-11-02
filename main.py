import gnupg
from pathlib import Path
import json
import jobsearch.gui.gui as gui
import platform
import argparse

import os
import configparser

def main(debug=False, config_file=None):
    config_parse = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config_parse.read(config_file)
    config = config_parse[platform.system()]

    gpg = gnupg.GPG(
        gnupghome=config.get("gnupghome", vars=os.environ),
        gpgbinary=config.get("gpgbinary", vars=os.environ)
        )
    LLM_API_key = None
    LLM_API_key_file = config.get("API_keys", vars=os.environ)
    with open(LLM_API_key_file, 'rb') as f:
        LLM_API_key = gpg.decrypt_file(f)
        LLM_API_key = json.loads(LLM_API_key.data)['google_gemini']
        
    gui.main(LLM_API_Key=LLM_API_key, debug=debug)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("-c","--config", default="./config.ini")
    args = parser.parse_args()

    main(debug=args.debug, config_file=args.config)