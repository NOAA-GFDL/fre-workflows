#!/usr/bin/env python
import os
import re
import metomi.rose.macro
import metomi.isodatetime.parsers as parse

class DateChecker(metomi.rose.macro.MacroBase):

    """Checks that dates that should be ISO8601 format are actually so
       - PP_START and PP_STOP
    """

    dates = ['PP_START', 'PP_STOP']

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        for item in self.dates:
            date_str = config.get_value(['template variables', item])

            if date_str is None:
                self.add_report('template variables', item, date_str,
                                f"Is required")
            elif date_str == "":
                self.add_report('template variables', item, date_str,
                                f"Should not be empty")
            else:
                try:
                    parse.TimePointParser().parse(date_str.strip('\'"'))
                except:
                    self.add_report('template variables', item, date_str,
                                    f"Invalid ISO8601 date")

        return self.reports
