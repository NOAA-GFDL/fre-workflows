#!/usr/bin/env python
import os
import re
import metomi.rose.macro
import metomi.isodatetime.parsers

class HeaderChecker(metomi.rose.macro.MacroBase):


    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        #Accepted configurations
        grids = {'native','regrid-xy/'}
        ignore = {'env','command'}

        #Looping over all headers and checking configurations
        for keys, sub_node in config.walk():

            if len(keys) == 1 and keys[0] not in ignore:
               
                grid = config.get_value([keys[0], 'grid'])
                if grid is None or grid not in grids:
                    if grid is None:
                        self.add_report(keys[0],'grid',grid,"Value required")
                    else:
                        self.add_report(keys[0],'grid',grid,"Not set correctly. Accepted values: native,regrid-xy")
                elif 'regrid-xy/' in grid:
                    if not grid.partition('regrid-xy/')[2] or grid.partition('regrid-xy/')[2].isspace():
                        self.add_report(keys[0],'grid',grid,"Value required ... ex:'regrid-xy/(SOMETHING)'")

                sources = config.get_value([keys[0], 'sources'])
                if sources is None:
                    self.add_report(keys[0],'sources',sources,"Value required")

                freq = config.get_value([keys[0], 'freq'])
                if freq is not None:
                    try:
                        metomi.isodatetime.parsers.DurationParser().parse(freq)
                    except:
                        self.add_report(keys[0],'freq',freq,"Not set correctly. Should be ISO8601 duration")

                chunk = config.get_value([keys[0], 'chunk'])
                if chunk is not None:
                    try:
                        metomi.isodatetime.parsers.DurationParser().parse(chunk)
                    except:
                        self.add_report(keys[0],'chunk',chunk,"Not set correctly. Should be ISO8601 duration")

        return self.reports
