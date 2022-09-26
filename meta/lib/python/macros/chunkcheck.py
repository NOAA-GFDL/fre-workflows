#!/usr/bin/env python
import os
import re
import metomi.rose.macro

"""
chunkcheck.py (rose) validates the values of PP_CHUNK_A and PP_CHUNK_B in rose-suite.conf. See class ChunkChecker for details. 
"""
# @file chunkcheck.py
# Author(s)
# Created by A.Radhakrishnan on 09/20/2022 
# Credit MSD workflow team

class ChunkChecker(metomi.rose.macro.MacroBase):

    """Validates rose-suite.conf to ensure the following: 
		PP_CHUNK_B must be a multiple of PP_CHUNK_A
       		PP_CHUNK_A must be a multiple of HISTORY_SEGMENT
       		PP_CHUNK_B is optional. PP_CHUNK_A is set to PP_CHUNK_B if the latter is absent 
    """
    def is_formatted_well(self, chunk):
              '''Takes in the chunk value and returns True or False based on the formatting '''
              pattern = r'[P]\d{1,3}[YDM]'
              chunk = re.sub('"', '', chunk)
              ret = False if (re.match(pattern, chunk) is None) else True
              return ret

    def is_multiple_of(self,chunk,chunkref):
        '''Takes in chunk value e.g P1Y and the chunk reference value from HISTORY_SEGMENT, returns True or False based on the validation to check if the former is a multiple of the latter''' 
        ret = True if(((int)(chunk[2]) % (int)(chunkref[2])) == 0) else False
        return ret

    def validate(self, config, meta_config=None):
        '''Takes in the config accessible via rose-suite.conf in main and opt,  Return a list of errors, if any upon validation'''

        #Get values of PP_CHUNK_A,B and HISTORY_SEGMENT from rose_suite.conf 
        try:
            pp_chunk_a = config.get_value(['template variables', 'PP_CHUNK_A'])
            pp_chunk_b = config.get_value(['template variables', 'PP_CHUNK_B'])
            history_seg = config.get_value(['template variables', 'HISTORY_SEGMENT'])
        except:
            self.add_report('Please check if values exist for PP_CHUNK_A PP_CHUNK_B HISTORY_SEGMENT in rose-suite.conf for your experiment') 
       
        #Raise error if PP_CHUNK_A value is not set
        if not pp_chunk_a:  
                   self.add_report('template variables', 
                                    pp_chunk_a, "PP_CHUNK_A-- must exist and set to ISO8601 duration of the desired post-processed output. e.g P1Y for one year chunk")
        else:
                           #Make sure PP_CHUNK_A is formatted as expected, check corresponding function
                           if(self.is_formatted_well(pp_chunk_a) == False):
                               self.add_report('Please check the value of PP_CHUNK_A and its formatting',pp_chunk_a)
                           #Make sure the PP chunk is a multiple of the history segment value PP chunk is a multiple of the history segment value 
                           if(self.is_multiple_of(pp_chunk_a,history_seg) == False):
                               self.add_report(pp_chunk_a, "needs to be a multiple of ", history_seg)
                           #If PP_CHUNK_B value is not set, assign PP_CHUNK_A to it 
                           if not pp_chunk_b:		
                               pp_chunk_b = pp_chunk_a
                           else: 
                               #If PP_CHUNK_B value exists, check formatting and ensure its a multiple of PP_CHUNK_A
                               if(self.is_formatted_well(pp_chunk_b) == False):
                                    self.add_report('Please check the value of PP_CHUNK_B and its formatting') 
                       
                               if(self.is_multiple_of(pp_chunk_b,pp_chunk_a) == False):
                                    self.add_report(pp_chunk_b, "needs to be a multiple of ", pp_chunk_a)
 

        return self.reports
