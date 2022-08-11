#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class FilesystemChecker(metomi.rose.macro.MacroBase):

    """Checks selected directories and files for readability/writability, if they are set:
    readable: GRID_SPEC, HISTORY_DIR, HISTORY_DIR_REFINED, PREANALYSIS_SCRIPT, REFINEDIAG_SCRIPT
    uses: meta/rose-meta.conf config 
    writable: PTMP_DIR, PP_DIR
    """

    readable = ['GRID_SPEC', 'HISTORY_DIR', 'HISTORY_DIR_REFINED', 'PREANALYSIS_SCRIPT', 'REFINEDIAG_SCRIPT']
    writable = ['PTMP_DIR', 'PP_DIR']

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # Check for readable files/dirs
        for item in self.readable:
            location = config.get_value(['template variables', item])
            if location:
                # resolve $USER or ${USER}
                location = re.sub('\${?USER}?', os.environ['USER'], location)
                # delete "$CYLC_WORKFLOW_RUN_DIR/" as a workaround
                # $CYLC_WORKFLOW_RUN_DIR is the Cylc-installed (running) copy of the source (editable) workflow dir
                # so if the validate script is run from the root source workflow dir, the location will match
                # TODO: find a better way as this is dependent on running the validation from the source root dir
                # Another clunky part of this is that the refinediag/preanalysis script locations are currently
                # set as \$CYLC_WORKFLOW_RUN_DIR, so the Cylc task uses the $CYLC_WORKFLOW_RUN_DIR variable that
                # does not exist outside of running Cylc jobs.
                location = re.sub('\\\\\$CYLC_WORKFLOW_RUN_DIR/', '', location)
                if os.access(location.strip('"'), os.R_OK):
                    pass
                else:
                    self.add_report('template variables', item, location,
                                    f"{item} must exist and be readable if set")

        # Check for writable files/dirs
        for item in self.writable:
            location = config.get_value(['template variables', item])
            if location:
                location = re.sub('\${?USER}?', os.environ['USER'], location)
                if os.access(location.strip('"'), os.W_OK):
                    pass
                else:
                    self.add_report('template variables', item, location,
                                    f"{item} must exist and be writable if set")

        return self.reports
