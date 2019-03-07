'''
    refreshes html file post build
'''
from os.path import isfile
from latenight.client import generate_name, generate_html_file

if __name__ == "__main__":
    print("-----> Starting post compile hook")
    print("-----> Generating webpage file")
    NAME = generate_name()
    _ = generate_html_file(NAME)
    if isfile(NAME):
        print("-----> File generation successful!")
