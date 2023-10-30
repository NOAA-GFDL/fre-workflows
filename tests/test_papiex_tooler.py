''' tests for PP/AN specific ops-tooling of job scripts for PAPIEX'''
import pytest

def test_import():
    ''' check that tool_ops_w_papiex functions can be imported '''
    from  lib.python.tool_ops_w_papiex import test_import
    assert(test_import() == 0)

def test_import_papiex_ops():
    ''' check that op list data can be imported '''
    import lib.python.papiex_ops as po
    assert ( all( [ po.op_list is not None,
                       len(po.op_list) > 0  ] ) )
