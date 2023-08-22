#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class FilesystemChecker(metomi.rose.macro.MacroBase):

    """Checks selected directories and files for readability/writability, if they are set:
    readable: GRID_SPEC, HISTORY_DIR, HISTORY_DIR_REFINED, PREANALYSIS_SCRIPT
    readable (spaced list): REFINEDIAG_SCRIPTS
    writable: PTMP_DIR, PP_DIR
    """

    readable = ['GRID_SPEC', 'HISTORY_DIR', 'HISTORY_DIR_REFINED', 'PREANALYSIS_SCRIPT', 'PP_GRID_SPEC']
    writable = ['PTMP_DIR', 'PP_DIR']
    readable_list = ['REFINEDIAG_SCRIPTS']

    def is_file_readable(self, filename):
        """Checks whether a candidate filename exists on the filesystem."""

        # resolve $USER or ${USER}
        location = re.sub('\${?USER}?', os.environ['USER'], filename)
        location = location.strip('"\'')
        # delete "$CYLC_WORKFLOW_RUN_DIR/" as a workaround
        # $CYLC_WORKFLOW_RUN_DIR is the Cylc-installed (running) copy of the source (editable) workflow dir
        # so if the validate script is run from the root source workflow dir, the location will match
        # TODO: find a better way as this is dependent on running the validation from the source root dir
        # Another clunky part of this is that the refinediag/preanalysis script locations are currently
        # set as \$CYLC_WORKFLOW_RUN_DIR, so the Cylc task uses the $CYLC_WORKFLOW_RUN_DIR variable that
        # does not exist outside of running Cylc jobs.
        location = re.sub('\$CYLC_WORKFLOW_RUN_DIR/', '', location)
        if os.access(location, os.R_OK):
            return True
        else:
            return False


    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # Check for readable files/dirs
        for item in self.readable:
            location = config.get_value(['template variables', item])
            if location is not None:
                if not self.is_file_readable(location):
                    self.add_report('template variables', item, location,
                                    f"{item} must exist and be readable if set")

        # Check for readable spaced lists of files/dirs
        for item in self.readable_list:
            locations = config.get_value(['template variables', item])
            if locations is not None:
                filenames = locations.split(' ')
                for filename in filenames:
                    filename.strip('\'\"')
                    if not self.is_file_readable(filename):
                        self.add_report('template variables', item, locations,
                                        f"{filename} must exist and be readable")

        # Check for writable files/dirs
        for item in self.writable:
            location = config.get_value(['template variables', item])
            if location is not None:
                location = re.sub('\${?USER}?', os.environ['USER'], location)
                if os.access(location.strip('"\''), os.W_OK):
                    pass
                else:
                    self.add_report('template variables', item, location,
                                    f"{item} must exist and be writable if set")

        return self.reports
