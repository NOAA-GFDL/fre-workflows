#!/usr/bin/env python
import os
import re
import metomi.rose.macro
import metomi.isodatetime.parsers as parse
import sys

"""
analysis_validator.py (rose) validates the DO_ANALYSIS and DO_ANALYSIS_ONLY specifications rose-suite.conf, and the corresponding dependencies and requirements.
"""
# @file analysis_validator.py
# Author(s)
# Created by A.Radhakrishnan on 03/15/2022 
# Credit MSD workflow team

class Analysis_Validator(metomi.rose.macro.MacroBase):

    """Validates analysis launching specifications to ensure the following: 
         IF DO_ANALYSIS and DO_ANALYSIS_ONLY are set to True, then ANALYSIS_DIR is writable 
         IF DO_ANALYSIS_ONLY is True, PP_DIR does not have to be writable. 
         FRE_ANALYSIS_HOME is valid 
         Script in app/analysis/rose-app.conf exists either in FRE_ANALYSIS_HOME or in file/
         component, freq in app/analysis/rose-app.conf for each analysis script is non-empty
          
    """

    def do_analysis_checks(self):
        '''
        '''
        big_chunk_days = big_chunk.get_days_and_seconds()[0]
        small_chunk_days = small_chunk.get_days_and_seconds()[0]
        if big_chunk_days % small_chunk_days == 0:
            return True
        else:
            return False

    def validate(self, config, meta_config=None):
        '''Takes in the config accessible via rose-suite.conf in main and opt,  Return a list of errors, if any upon validation'''
        
        DO_ANALYSIS = config.get_value(['template variables', 'DO_ANALYSIS'])
        DO_ANALYSIS_ONLY = config.get_value(['template variables', 'DO_ANALYSIS_ONLY'])

        if (DO_ANALYSIS or DO_ANALYSIS_ONLY):
            try:
               analysis_dir = config.get_value(['template variables', 'ANALYSIS_DIR'])
            except:
                self.add_report(
                    'template variables', 'ANALYSIS_DIR', analysis_dir,
                    "Required and not set")
            if (analysis_dir is not None):
              if os.access(analysis_dir, os.W_OK):
                pass
              else:
                self.add_report('template variables', "ANALYSIS_DIR", analysis_dir,"ANALYSIS_DIR must exist and be writable if set")
            else: 
                self.add_report(
                'template variables', 'ANALYSIS_DIR', analysis_dir,
                "Required and not set") 

        return self.reports
