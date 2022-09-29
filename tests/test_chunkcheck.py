#test chunkcheck.py macro

import pytest
from meta.lib.python.macros.chunkcheck import ChunkChecker

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
