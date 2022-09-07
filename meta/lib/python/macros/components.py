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

        # Retrieve the CONFIG_COMPS setting, which is a pointer to the desired remap-pp-component configuration
        config_key = config.get_value(['template variables', 'CONFIG_COMPS'])

        # If it does not exist, then skip- probably in the default settings which lack the CONFIG_COMPS setting
        if config_key:
            config_key = config_key.strip('"')
        else:
            return self.reports

        # Read the Rose app configuration specified by config_key
        # NOTE: Next line is a workaround. We want to use the load_with_opts to handle the configuration overrides but the function does not exist
        # https://metomi.github.io/rose/2019.01.2/html/api/configuration/api.html#rose.config.ConfigLoader.load_with_opts
        # The main problem is that the main config file is ignored, and it should be the defaults.
        path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/remap-pp-components/opt/rose-app-' + config_key + '.conf'
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
