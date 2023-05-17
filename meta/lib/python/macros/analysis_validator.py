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
         TODO IF DO_ANALYSIS_ONLY is True, PP_DIR does not have to be writable. 
         FRE_ANALYSIS_HOME is valid 
         Script in app/analysis/rose-app.conf exists either in FRE_ANALYSIS_HOME or in file/
         script, component, freq in app/analysis/rose-app.conf for each analysis script is non-empty
          
    """
    def validate(self, config, meta_config=None):
        '''Takes in the config accessible via rose-suite.conf in main and opt,  Return a list of errors, if any upon validation'''
        do_analysis = config.get_value(['template variables', 'DO_ANALYSIS'])
        do_analysis_only = config.get_value(['template variables', 'DO_ANALYSIS_ONLY'])
        if do_analysis == "True":
            do_analysis = bool(1)
        else:
            do_analysis = bool(0)
        if do_analysis_only == "True":
            do_analysis_only = bool(1)
        else:
            do_analysis_only = bool(0)
        #Validation: ANALYSIS_DIR exists and is valid or not depending on the configuration settings used 
        if do_analysis_only and not do_analysis:
            self.add_report(
                'template variables', 'DO_ANALYSIS', do_analysis,
                "Must be set if DO_ANALYSIS_ONLY is set")
        if do_analysis:
            try:
               analysis_dir = config.get_value(['template variables', 'ANALYSIS_DIR'])
            except:
                self.add_report(
                    'template variables', 'ANALYSIS_DIR', analysis_dir,
                    "Must exist and be writable if DO_ANALYSIS is set")
            if (analysis_dir is not None):
              analysis_dir = os.path.expandvars(analysis_dir)
              #todo trailing slash addition if it does not exist
              if os.access(analysis_dir.strip('"'), os.W_OK): 
                pass
              else:
                self.add_report('template variables', "ANALYSIS_DIR", analysis_dir,"ANALYSIS_DIR must exist and be writable if DO_ANALYSIS is set")
            else: 
                self.add_report(
                'template variables', 'ANALYSIS_DIR', analysis_dir,
                "Must exist and be writable if DO_ANALYSIS is set")
        # Validation:  FRE_ANALYSIS_HOME accessible or not 
        fre_analysis_home = config.get_value(['template variables', 'FRE_ANALYSIS_HOME'])
        if (fre_analysis_home is not None):
              if os.access(fre_analysis_home.strip('"'), os.R_OK):
                pass
              else:
                self.add_report('template variables', "FRE_ANALYSIS_HOME", fre_analysis_home,"FRE_ANALYSIS_HOME must be readable if set")
        # Validation: This snippet checks if there freq, script and comp for every analysis definition in app/analysis/rose-app.conf. If not, a validation error is thrown. 
        app_analysis_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/analysis/rose-app.conf'
        required_val = ['freq','script','components']
        report_dict = {} 
        try:
            config_node = ConfigLoader.load(app_analysis_conf)
        except:
            sys.exit("Unable to read analysis rose-app.conf")
        for keys, sub_node in config_node.walk():
          report_val = []
          item = keys[0]
          # skip these config stanza headers as they are not analysis scripts
          if item == "env" or item == "command":
              continue 
          for val in required_val:
            analysis_defn = config_node.get_value(keys=[item, val])
            if(analysis_defn is None):
               report_val.append(val)
               report_dict[item]=report_val   
               self.add_report(
                   'template variables','app/analysis/rose-app.conf', item+"/"+val, 
                   "Required and not set")
        # Validation: Check if the paths to the analysis scripts exist referring rose-app.conf in app/analysis. Scripts may either exist in FRE_ANANALYSIS_HOME or in file/ within the analysis app or absolute paths 
          ascript = config_node.get_value(keys=[item, "script" ]) 
          if(ascript is not None):
            # check if its readable 
            if(ascript is not None):
               if os.access(ascript, os.R_OK):
                  pass
               #when its in FRE_ANALYSIS_HOME 
               elif(ascript.startswith("$FRE_ANALYSIS_HOME")):
                  if(fre_analysis_home is None):
                         fre_analysis_home = "$FRE_ANALYSIS_HOME"    
                  ascript = ascript.replace("$FRE_ANALYSIS_HOME", fre_analysis_home.strip('"'))
               else: 
                  #in file/    
                  analysis_file_suffix = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/analysis/file/'
                  ascript = analysis_file_suffix+ascript
            if os.access(ascript, os.R_OK):
                  pass
            else:
                  self.add_report(
                   'template variables','app/analysis/rose-app.conf', f"{item}:{ascript}",
                   "Not readable")
             
        return(self.reports) #TODO return error just once 
