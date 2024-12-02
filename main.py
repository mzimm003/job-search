from jobsearch.gui.gui import GUI
from jobsearch.backend.backend import Backend
import argparse

def main(debug=False, config_dir=None, user=""):

    be = Backend(configuration_dir=config_dir, user=user)
    gui = GUI(backend=be, debug=debug)
    gui.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true')
    parser.add_argument("-c","--config-dir", default="./jobs")
    parser.add_argument("-u","--user", default="mzimm003@gmail.com")
    args = parser.parse_args()

    main(debug=args.debug, config_dir=args.config_dir, user=args.user)