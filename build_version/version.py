import json
import os
import re
import argparse
import sys
import logging


def find_version(verdir):
    filedict = {}
    for root, directory, files in os.walk(verdir):
        for afile in files:
            if not os.path.islink(afile):
                if afile.startswith("Build") and afile.endswith("dmg"):
                    version = afile.split('Build-')[1].split('.dmg')[0]
                    verlist = version.split('.')
                    for i in range(1, 3):
                        try:
                            verlist[i] = verlist[i].rjust(2, "0")
                        except BaseException:
                            verlist.append("00")
                    realversion = int(''.join(verlist))
                    logging.debug(
                        "Version number is {}" .format(
                            int(realversion)))
                    filedict[afile] = realversion

    for version in sorted(filedict, key=filedict.get, reverse=True):
        print version


def main():
    parser = argparse.ArgumentParser(
        description='Show Builds with version in sorted order')
    parser.add_argument("--source", dest="sourcedir",
                        help='source directory where all builds are located')
    args = parser.parse_args()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    sourcedir = args.sourcedir
    if os.path.exists(os.path.abspath(sourcedir)):
        find_version(sourcedir)
    else:
        raise Exception(
            "Source Directory Does not exist, Please check the directory name")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
