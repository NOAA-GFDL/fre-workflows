#!/usr/bin/env python
import os
import re
import metomi.rose.macro
import metomi.isodatetime.parsers as parse
import sys

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

    def is_multiple_of(self,chunk,chunkref=None):
       '''Takes in chunk value e.g P1Y and the chunk reference value from HISTORY_SEGMENT, returns True or False based on the validation to check if the former is a multiple of the latter'''
       #extract numbers from PP_CHUNK_A,B or HISTORY_SEGMENT
       pp_duration = None
       ret = False
       historyseg_duration = None
       try: 
          pp_duration = parse.DurationParser().parse(chunk)
       except Exception as e:
          self.add_report('template variables',"PP_CHUNK_A(or B)",chunk,'Please check the value of chunk specifications and its formatting')
       if(pp_duration is not None and chunkref is not None): 
           ppd = pp_duration.get_days_and_seconds()
           try:
               historyseg_duration = parse.DurationParser().parse(chunkref)
           except Exception as e :
               self.add_report('template variables',"HISTORY_SEGMENT",chunkref,e)
           if(historyseg_duration is not None):
               hsd = historyseg_duration.get_days_and_seconds()
               ppd_days = ppd[0] 
               if(ppd_days % 365 == 0) & (hsd[0] % 365 != 0):
                   ppd_days = ppd_days - (5 * (ppd_days/365) )  
                   print("Setting ",ppd[0],"to ",ppd_days) 
               ret = True if(((int)(ppd_days) % (int)(hsd[0])) == 0) else False
       return ret

    def validate(self, config, meta_config=None):
        '''Takes in the config accessible via rose-suite.conf in main and opt,  Return a list of errors, if any upon validation'''

        #Get values of PP_CHUNK_A,B and HISTORY_SEGMENT from rose_suite.conf 
        try:
            pp_chunk_a = config.get_value(['template variables', 'PP_CHUNK_A'])
            pp_chunk_b = config.get_value(['template variables', 'PP_CHUNK_B'])
            history_seg = config.get_value(['template variables', 'HISTORY_SEGMENT'])
        except:
            print('Please check if values exist for PP_CHUNK_A PP_CHUNK_B HISTORY_SEGMENT in rose-suite.conf for your experiment') 
        pp_chunk_a = pp_chunk_a.strip('\"')
        pp_chunk_b = pp_chunk_b.strip('\"') 
        history_seg = history_seg.strip('\"')
        #Make sure the PP chunk is a multiple of the history segment value PP chunk is a multiple of the history segment value 
        if(self.is_multiple_of(pp_chunk_a,history_seg) == False):
           self.add_report('template variables',"PP_CHUNK_A",pp_chunk_a, "Duration in days MUST exist and needs to be a multiple of HISTORY_SEGMENT:"+history_seg)
        #If P_CHUNK_B value is not set, assign PP_CHUNK_A to it 
        if not pp_chunk_b or pp_chunk_b == "":
            print("INFO: No value found for PP_CHUNK_B. Workflow will assign PP_CHUNK_A to PP_CHUNK_B")	
            pp_chunk_b = pp_chunk_a
        else: 
            if(self.is_multiple_of(pp_chunk_b,pp_chunk_a) == False):
                self.add_report("template variables","PP_CHUNK_B", pp_chunk_b, "Duration in days (if exists) needs to be a multiple of PP_CHUNK_A:"+pp_chunk_a)
        return self.reports
