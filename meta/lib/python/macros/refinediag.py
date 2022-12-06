#!/usr/bin/env python
import re
import os
import metomi.rose.macro

class RefineDiagChecker(metomi.rose.macro.MacroBase):

    """Checks options related to refineDiag:
       Uses: meta/rose-meta.conf
    1. If either refinediag or preanalysis is switched on, then experiment, gridspec, platform, and target must be set
    2. If refinediag is switched on, then refinediagdir must be set, and must be writable
    3. If refinediag is switched on, then refinediag_scripts must be set
    4. If preanalysis is switched on, then preanalysis_script must be set
    """

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # Check if refinediag/preanalysis switches are set
        do_refinediag = config.get_value(['template variables', 'DO_REFINEDIAG'])
        do_preanalysis = config.get_value(['template variables', 'DO_PREANALYSIS'])
        if do_refinediag == "True":
            do_refinediag = bool(1)
        else:
            do_refinediag = bool(0)
        if do_preanalysis == "True":
            do_preanalysis = bool(1)
        else:
            do_preanalysis = bool(0)

        # If refinediag is on, then refinediagdir must be writable
        if do_refinediag:
            refine_dir = config.get_value(['template variables', 'HISTORY_DIR_REFINED'])
            if refine_dir:
                # resolve $USER or ${USER}
                refine_dir = re.sub('\${?USER}?', os.environ['USER'], refine_dir)
                # First do a mkdir -p which will pass if it exists but not writable
                # Then test the directory writability
                refine_dir = refine_dir.strip('"')
                try:
                    os.makedirs(refine_dir, exist_ok=True)
                    if os.access(refine_dir, os.W_OK):
                        pass
                    else:
                        self.add_report('template variables', 'HISTORY_DIR_REFINED', refine_dir,
                                        "HISTORY_DIR_REFINED must exist and be writable when DO_REFINEDIAG is on")
                except:
                    self.add_report('template variables', 'HISTORY_DIR_REFINED', refine_dir,
                                    "HISTORY_DIR_REFINED must exist and be writable when DO_REFINEDIAG is on")
            else:
                self.add_report(
                    "template variables", "HISTORY_DIR_REFINED", None,
                    "HISTORY_DIR_REFINED must be set when DO_REFINEDIAG is on")

        # If either refinediag or preanalysis is on, then experiment/gridspec/platform/target must also be set
        if do_refinediag or do_preanalysis:
            required = ['EXPERIMENT', 'PLATFORM', 'TARGET', 'GRID_SPEC']
            for item in required:
                if config.get_value(['template variables', item]):
                    pass
                else:
                    self.add_report(
                        "template variables", item, None,
                        f"{item} must be set if either DO_REFINEDIAG or DO_PREANALYSIS is set")

        # If refinediag is on, then refinediag_script and refinediag_name must also be set
        if do_refinediag:
            required = ['REFINEDIAG_SCRIPTS']
            for item in required:
                if config.get_value(['template variables', item]):
                    pass
                else:
                    self.add_report(
                        "template variables", item, None,
                        f"{item} must be set if DO_REFINEDIAG is set")

        # If preanalysis is on, then preanalysis_script and preanalysis_name must also be set
        if do_preanalysis:
            required = ['PREANALYSIS_SCRIPT']
            for item in required:
                if config.get_value(['template variables', item]):
                    pass
                else:
                    self.add_report(
                        "template variables", item, None,
                        f"{item} must be set if DO_PREANALYSIS is set")

        return self.reports
