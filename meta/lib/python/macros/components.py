#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class ComponentChecker(metomi.rose.macro.MacroBase):

    """Checks for configuration consistency for settings related to components
    1. Requested components in rose-suite.conf must exist in remap-pp-component's app config
    """

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # If PP_COMPONENTS is not set, assume we're in the default config and exit
        if not config.get_value(['template variables', 'PP_COMPONENTS']):
            return self.reports

        # Read the Rose app configuration specified by config_key
        path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/remap-pp-components/rose-app.conf'
        node = metomi.rose.config.load(path_to_conf)

        # Retrieve the Rose app components
        # The keys in the Rose app config are the component, with optional ".suffix".
        available_comps = set()
        regex_pp_comp = re.compile('^\w+')
        for keys, sub_node in node.walk():
            # only target the keys
            if len(keys) != 1:
                continue
            # skip env and command keys
            item = keys[0]
            if item == "env" or item == "command":
                continue
            comp = regex_pp_comp.match(item).group()
            available_comps.add(comp)
        #print(available_comps)

        # Requested components (PP_COMPONENTS) in rose-suite.conf must exist in remap-pp-component's app config
        requested_comps = config.get_value(['template variables', 'PP_COMPONENTS']).strip('"').split(' ')

        # Check each component for definition in remap-pp-component's config
        for comp in requested_comps:
            if comp in available_comps:
                pass
            else:
                self.add_report( "template variables", "PP_COMPONENTS", config.get_value(['template variables', 'PP_COMPONENTS']).strip('"'), f"Requested component '{comp}' is not defined in {path_to_conf}")

        return self.reports
