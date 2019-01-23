#!/usr/bin/env python

# Copyright 2018-2019 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import io
import sys

import nbformat


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", metavar="EXECUTED_NOTEBOOK")
    args = parser.parse_args(sys.argv[1:])
    with io.open(args.notebook, "rt") as f:
        nb = nbformat.read(f, nbformat.current_nbformat)
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        outputs = cell.get("outputs")
        if outputs:
            for o in outputs:
                if o.output_type == "error":
                    raise RuntimeError("%s has one or more errors" %
                                       (args.notebook,))
    sys.stdout.write("OK\n")
