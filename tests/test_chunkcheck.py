#test chunkcheck.py macro

import pytest
from meta.lib.python.macros.chunkcheck import ChunkChecker
from metomi.rose.config import load, ConfigNode 
import configparser

def tests_is_multiple_of(): 
   '''Verify True return state of `is_multiple_of`''' 
   cc = ChunkChecker()
   output = cc.is_multiple_of('P1W','P1D')
   assert output == True

def teste_is_multiple_of():
   '''Verify (exception case) True return state of `is_multiple_of`'''
   cc = ChunkChecker()
   output = cc.is_multiple_of('P1Y','P1M')
   assert output == True 

def testf_is_multiple_of():
   '''Verify False return state of `is_multiple_of`'''
   cc = ChunkChecker()
   output = cc.is_multiple_of('P5D','P1W')
   assert output == False

def testf_suiteload():
   '''load a suite with validation issue '''
   config_node = ConfigNode()
   cc = ChunkChecker()
   config = config_node.set(keys=['template variables','PP_CHUNK_A'], value='P1M')
   config = config_node.set(keys=['template variables','PP_CHUNK_B'], value='P1M') 
   config = config_node.set(keys=['template variables','HISTORY_SEGMENT'], value='P1Y') 
   output = cc.validate(config)
   assert "MUST exist and needs to be a multiple of HISTORY_SEGMENT" in str(output)

def tests_suiteload():
   '''load a suite with validation issue '''
   config_node = ConfigNode()
   cc = ChunkChecker()
   config = config_node.set(keys=['template variables','PP_CHUNK_A'], value='P1Y')
   config = config_node.set(keys=['template variables','PP_CHUNK_B'], value='P1Y')
   config = config_node.set(keys=['template variables','HISTORY_SEGMENT'], value='P1M')
   output = cc.validate(config)
   assert len(output) == 0 
