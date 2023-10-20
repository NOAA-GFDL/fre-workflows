#!/app/conda/miniconda/envs/cylc/bin/python

import os
lib_python_path=str(os.environ.get('PWD'))+'/lib/python'

import sys
sys.path.append(lib_python_path)

def test_import():
    import tool_ops_w_papiex
    assert(tool_ops_w_papiex.test_import() == 0)

