#!/usr/bin/env python
# Generate set of projects mk files. 
# Usage: python generate_mk.py PROJECTS_MK_DIR  THRUST_SOURCE_DIR
#   The program scans through unit tests and examples in THRUST_SOURCE_DIR
#   and generates project mk for each of the tests and examples in PROJECTS_MK_DIR
#   A single example or unit test source file generates its own executable
#   This program is called by a top level Makefile, but can also be used stand-alone for debugging
#   This program also generates testing.mk, examples.mk and dependencies.mk
from __future__ import print_function
import sys
import shutil as sh
import os
import glob
import re

test_template = """
TEST_SRC   := %(TEST_SRC)s
TEST_NAME  := %(TEST_NAME)s
include $(ROOTDIR)/thrust/internal/build/generic_test.mk
"""
example_template = """
EXAMPLE_SRC   := %(EXAMPLE_SRC)s
EXAMPLE_NAME  := %(EXAMPLE_NAME)s
include $(ROOTDIR)/thrust/internal/build/generic_example.mk
"""

def Glob(pattern, directory,exclude='\B'):
    src = glob.glob(os.path.join(directory,pattern))
    p = re.compile(exclude)
    src = [s for s in src if not p.match(s)]
    return src


def generate_test_mk(mk_path, test_path, group, TEST_DIR):
    print(f'Generating makefiles in "{mk_path}" for tests in "{test_path}"')
    src_cu  = Glob("*.cu",  test_path, ".*testframework.cu$")
    src_cxx = Glob("*.cpp", test_path)
    src_cu.sort();
    src_cxx.sort();
    src_all = src_cu + src_cxx;
    tests_all = []
    dependencies_all = []
    for s in src_all:
        fn = os.path.splitext(os.path.basename(s));
        t = f"thrust.{group}.{fn[0]}"
        e = fn[1]
        mkfile = test_template % {"TEST_SRC" : s,  "TEST_NAME" : t}
        with open(os.path.join(mk_path, f"{t}.mk"), 'w') as f:
            f.write(mkfile)
        tests_all.append(os.path.join(mk_path,t))
        dependencies_all.append(f"{t}: testframework")
    return [tests_all, dependencies_all]

def generate_example_mk(mk_path, example_path, group, EXAMPLE_DIR):
    print(f'Generating makefiles in "{mk_path}" for examples in "{example_path}"')
    src_cu  = Glob("*.cu",  example_path)
    src_cxx = Glob("*.cpp", example_path)
    src_cu.sort();
    src_cxx.sort();
    src_all = src_cu + src_cxx;
    examples_all = []
    for s in src_all:
        fn = os.path.splitext(os.path.basename(s));
        t = f"thrust.{group}.{fn[0]}"
        e = fn[1]
        mkfile = example_template % {"EXAMPLE_SRC" : s, "EXAMPLE_NAME" : t}
        with open(os.path.join(mk_path, f"{t}.mk"), 'w') as f:
            f.write(mkfile)
        examples_all.append(os.path.join(mk_path,t))
    return examples_all


## relpath : backported from os.relpath form python 2.6+
def relpath(path, start):
    """Return a relative version of a path"""

    import posixpath
    if not path:
        raise ValueError("no path specified")
    start_list = posixpath.abspath(start).split(posixpath.sep)
    path_list = posixpath.abspath(path).split(posixpath.sep)
    # Work out how much of the filepath is shared by start and path.
    i = len(posixpath.commonprefix([start_list, path_list]))
    rel_list = [posixpath.pardir] * (len(start_list)-i) + path_list[i:]
    return posixpath.curdir if not rel_list else posixpath.join(*rel_list)

mk_path=sys.argv[1]
REL_DIR="../../"
if (len(sys.argv) > 2):
    root_path=sys.argv[2];
    mk_path = relpath(mk_path, root_path)
    REL_DIR = relpath(root_path,mk_path)

try:
    sh.rmtree(mk_path)
except:
    pass
os.makedirs(mk_path)

tests_all, dependencies_all = generate_test_mk(mk_path, "testing/", "test", REL_DIR)
tests_cu,  dependencies_cu  = generate_test_mk(mk_path, "testing/cuda/", "test.cuda", REL_DIR)
tests_all.extend(tests_cu)
dependencies_all.extend(dependencies_cu)

testing_mk = (
    "".join(f"PROJECTS += {t}" + "\n" for t in tests_all)
    + "PROJECTS += internal/build/testframework\n"
)
with open(os.path.join(mk_path,"testing.mk"),'w') as f:
    f.write(testing_mk)
dependencies_mk = "".join(d + "\n" for d in dependencies_all)
with open(os.path.join(mk_path,"dependencies.mk"),'w') as f:
    f.write(dependencies_mk)
examples_all  = generate_example_mk(mk_path, "examples/", "example", REL_DIR)
examples_cuda = generate_example_mk(mk_path, "examples/cuda/", "example.cuda", REL_DIR)
examples_all.extend(examples_cuda)
examples_mk = "".join(f"PROJECTS += {e}" + "\n" for e in examples_all)
with open(os.path.join(mk_path,"examples.mk"),'w') as f:
    f.write(examples_mk)








