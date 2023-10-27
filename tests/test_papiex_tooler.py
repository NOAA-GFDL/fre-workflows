''' tests for PP/AN specific ops-tooling of job scripts for PAPIEX'''
import pytest

def test_import():
    ''' check that tool_ops_w_papiex functions can be imported '''
    from  lib.python.tool_ops_w_papiex import test_import
    assert(test_import() == 0)

