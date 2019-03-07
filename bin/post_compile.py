'''
    refreshes html file post build
'''
import sys
sys.path.append("./latenight")

from os.path import isfile
from client import generate_name, generate_html_file

if __name__ == "__main__":
    print("-----> Starting post compile hook")
    print("-----> Generating webpage file")
    NAME = generate_name()
    _ = generate_html_file(NAME)
    if isfile(NAME):
        print("-----> File generation successful!")
