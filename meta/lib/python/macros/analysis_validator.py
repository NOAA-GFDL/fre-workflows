#!/usr/bin/env python
import os
import json
import metomi.rose.macro
from metomi.rose.macro import *
import metomi.rose.config as ConfigLoader
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
        # Report: Script location checks: uses FRE_ANALYSIS_HOME
        fre_analysis_home = config.get_value(['template variables', 'FRE_ANALYSIS_HOME'])
        if (fre_analysis_home is not None):
              if os.access(fre_analysis_home, os.R_OK):
                pass
              else:
                self.add_report('template variables', "FRE_ANALYSIS_HOME", fre_analysis_home,"FRE_ANALYSIS_HOME must exist and be readable if set")
        # Validation: Check if the paths to the analysis scripts exist referring rose-app.conf in app/analysis. Scripts may either exist in FRE_ANANALYSIS_HOME or in files/ within the postprocessing repo
        app_analysis_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/analysis/rose-app.conf'
        # This snippet checks if there freq, script and comp for every analysis definition in app/analysis/rose-app.conf. If not, a validation error is thrown. 
        required_val = ['freq','script','components']
        report_dict = {} 
        try:
            config_node = ConfigLoader.load(app_analysis_conf)
        except:
            sys.exit("Un$able to read analysis rose-app.conf")
        for keys, sub_node in config_node.walk():
          report_val = []
          item = keys[0] 
          for val in required_val:
            analysis_defn = config_node.get_value(keys=[item, val])
            if(analysis_defn is None):
               report_val.append(val)
               report_dict[item]=report_val   
        if report_dict: 
          self.add_report(
                'template variables','app/analysis/rose-app.conf', item+"/"+val, 
                "Required and not set")
        return(self.reports) 
