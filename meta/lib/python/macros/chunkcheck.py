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

    def is_multiple_of(self, big_chunk, small_chunk):
        '''Takes in chunk value e.g P1Y and the chunk reference value from HISTORY_SEGMENT, returns True or False based on the validation to check if the former is a multiple of the latter'''
	big_chunk_months = big_chunk.years*12 + big_chunk.months
        small_chunk_months = small_chunk.years*12 + small_chunk.months
        if big_chunk_months % small_chunk_months == 0:
            return True
        else:
            return False

    def validate(self, config, meta_config=None):
        '''Takes in the config accessible via rose-suite.conf in main and opt,  Return a list of errors, if any upon validation'''

        # history_segment and pp_chunk_a are required and must be iso8601-parsable
        # if missing, add reports and exit early
        history_segment = config.get_value(['template variables', 'HISTORY_SEGMENT'])
        history_segment_duration = None
        if history_segment:
            history_segment = history_segment.strip('\'\"')
            try:
                history_segment_duration = parse.DurationParser().parse(history_segment)
            except:
                self.add_report(
                    'template variables', 'HISTORY_SEGMENT', history_segment,
                    "Could not be parsed as ISO8601 duration")
        else:
            self.add_report(
                'template variables', "HISTORY_SEGMENT", history_segment,
                "Required and not set")

        pp_chunk_a = config.get_value(['template variables', 'PP_CHUNK_A'])
        pp_chunk_a_duration = None
        if pp_chunk_a:
            pp_chunk_a = pp_chunk_a.strip('\"\'')
            try:
                pp_chunk_a_duration = parse.DurationParser().parse(pp_chunk_a)
            except:
                self.add_report(
                    'template variables', 'PP_CHUNK_A', pp_chunk_a,
                    "Could not be parsed as ISO8601 duration")
        else:
            self.add_report(
                'template variables', "PP_CHUNK_A", pp_chunk_a,
                "Required and not set")

        if not history_segment_duration or not pp_chunk_a_duration:
            return self.reports


        # check chunk_a and history_segment consistency
        if not self.is_multiple_of(pp_chunk_a_duration, history_segment_duration):
            self.add_report(
                'template variables', "PP_CHUNK_A", pp_chunk_a,
                f"Must be a multiple of HISTORY_SEGMENT ({history_segment})")

        # if chunk_b is set, check chunk_a and chunk_b consistency
        pp_chunk_b = config.get_value(['template variables', 'PP_CHUNK_B'])
        if pp_chunk_b:
            pp_chunk_b = pp_chunk_b.strip('\"') 
            pp_chunk_b_duration = None
            try:
                pp_chunk_b_duration = parse.DurationParser().parse(pp_chunk_b)
            except:
                self.add_report(
                    'template variables', 'PP_CHUNK_B', pp_chunk_b,
                    "Could not be parsed as ISO8601 duration")
            if pp_chunk_b_duration:
                if (pp_chunk_b_duration == pp_chunk_a_duration):
                    self.add_report(                        
                        "template variables", "PP_CHUNK_B", pp_chunk_b, 
                        f"If set, PP_CHUNK_B must not be equivalent to PP_CHUNK_A ({pp_chunk_a})")
                if not self.is_multiple_of(pp_chunk_b_duration, pp_chunk_a_duration):
                    self.add_report(
                        "template variables", "PP_CHUNK_B", pp_chunk_b,
                        f"If set, PP_CHUNK_B must be a multiple of PP_CHUNK_A ({pp_chunk_a})")

        return self.reports
