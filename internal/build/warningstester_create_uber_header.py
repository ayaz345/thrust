'''
Helper script for creating a header file that includes all of Thrust's
public headers.  This is useful for instance, to quickly check that
all the thrust headers obey proper syntax or are warning free.

This script simply outputs a list of C-style #include's to the standard
output--this should be redirected to a header file by the caller.
'''

import sys
import os
import re
from stat import *

thrustdir = sys.argv[1]

def find_headers(base_dir, rel_dir, exclude = ['\B']):
    '''
    Recursively find all *.h files inside base_dir/rel_dir,
    except any that match the exclude regexp list
    '''
    assert(type(exclude) == list)
    full_dir = f'{base_dir}/{rel_dir}'
    result = []
    for f in os.listdir(full_dir):
        rel_file = f'{rel_dir}/{f}'
        for e in exclude:
            if re.match(e, rel_file):
                break
        else:
            if f.endswith('.h'):
                result.append(rel_file)
            elif S_ISDIR(os.stat(f'{full_dir}/{f}').st_mode):
                result.extend(find_headers(base_dir, rel_file, exclude))
    return result

print(f'/* File is generated by {sys.argv[0]} */')

exclude_re = ['.*/detail$',
              'thrust/iterator',
              'thrust/random',
              'thrust/system/tbb']
headers = find_headers(thrustdir, 'thrust', exclude_re)

if len(headers) == 0:
    print('#error no include files found\n')

print('#define THRUST_CPP11_REQUIRED_NO_ERROR')
print('#define THRUST_CPP14_REQUIRED_NO_ERROR')
print('#define THRUST_MODERN_GCC_REQUIRED_NO_ERROR')
for h in headers:
    print(f'#include <{h}>')

exit()
