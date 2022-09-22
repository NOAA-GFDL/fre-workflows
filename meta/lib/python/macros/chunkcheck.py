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
    def is_formatted_well(self, pp_chunk_a):
               

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # Check for readable files/dirs
        pp_chunk_a = config.get_value(['template variables', 'PP_CHUNK_A'])
        pp_chunk_b = config.get_value(['template variables', 'PP_CHUNK_B'])
        history_seg = config.get_value(['template variables', 'HISTORY_SEGMENT'])

        if not pp_chunk_a:  
                   self.add_report('template variables', 
                                    pp_chunk_a, "must exist and set to ISO8601 duration of the desired post-processed output. e.g P1Y for one year chunk")
        else:
                           if(self.is_formatted_well(pp_chunk_a) == False):
                               self.add_report('Please check the value of PP_CHUNK_A and its formatting')
                           if(self.is_multiple_of(pp_chunk_a,history_seg) == False):
                               self.add_report(pp_chunk_a, "needs to be a multiple of ", history_seg)

			   if not pp_chunk_b:		
                               pp_chunk_b = pp_chunk_a
                           else: 
                               if(self.is_formatted_well(pp_chunk_b) == False):
                                    self.add_report('Please check the value of PP_CHUNK_B and its formatting') 
                       
                               if(self.is_multiple_of(pp_chunk_b,pp_chunk_a) == False):
                                    self.add_report(pp_chunk_b, "needs to be a multiple of ", pp_chunk_a)
 

        return self.reports
