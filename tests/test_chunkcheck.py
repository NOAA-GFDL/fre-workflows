#test chunkcheck.py macro

import pytest
from meta.lib.python.macros.chunkcheck import ChunkChecker

def testf_is_formatted_well():
   '''Verify False return state of `is_formatted_well`'''
   cc = ChunkChecker()
   output = cc.is_formatted_well('P1Yk')
   assert output == False

def tests_is_formatted_well():
   '''Verify True return state of `is_formatted_well`'''

   cc = ChunkChecker()
   output = cc.is_formatted_well('P1Y')
   assert output == True

def tests_is_multiple_of(): 
   '''Verify True return state of `is_multiple_of`''' 
   cc = ChunkChecker()
   output = cc.is_multiple_of('P4Y','P1Y')
   assert output == True

def testf_is_multiple_of():
   '''Verify False return state of `is_multiple_of`'''
   cc = ChunkChecker()
   output = cc.is_multiple_of('P12Y','P5Y')
   assert output == False 
