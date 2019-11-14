"""
File to modify the YML file compatible with windows
It remove all the version number of teh package

- bokeh=1.3.4=py_0

become:

- bokeh

add remove some package
"""

import sys
import fileinput

file_path_input="paralogger_test.yml"
file_path_output = "pataloger_out.yml"

f=  open(file_path_output, "w")

list_to_remove = [
"gstreamer",
"libedit",
"libgfortran-ng",
"libgcc-ng",
"gst-plugins-base",
"readline",
"libstdcxx-ng",
"ncurses",
"dbus",
"libuuid"]


# replace all occurrences of 'sit' with 'SIT' and insert a line after the 5th
for i, line in enumerate(fileinput.input(file_path_input)):

    if "=" in line:
        first_part = line.split('=')[0]
        print(first_part)
        for elem in list_to_remove:
            if  elem in first_part:
                print("ignore :" + str(first_part))
                first_part = ""
        f.write(first_part +"\n")
    else:
        print(line)
        f.write(line)




    # sys.stdout.write(line.replace('sit', 'SIT'))  # replace 'sit' and write
    # if i == 4: sys.stdout.write('\n')  # write a blank line after the 5th line