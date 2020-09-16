from __future__ import print_function
import os
import shutil
import glob2

ss = 'entry not found'
datafile = "D:/CIA/CIA/test/080920/2020-09-08/2020-09-08.txt"
path_to_file = "D:/CIA/CIA/test/080920/2020-09-08/dev.txt"
print(ss)
print(datafile)
def s_1():
    with open(datafile, 'r', encoding='utf-8') as infile,open(path_to_file, 'w+', encoding='utf-8') as outfile:
        str_01 = []
        str_line = []
        for line in infile:
            if " Glory.DeviceController |" in line:
                if ss in line:
                    str_line = line.split('|')
                    str_01.append(str_line[6])


        seen = set()
        uniq_session_id = [x for x in str_01 if x not in seen and not seen.add(x)]

        for elem in uniq_session_id:
            outfile.write(elem + '\n')
        print(len(str_01))

s_1()