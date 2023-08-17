#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class ComponentChecker(metomi.rose.macro.MacroBase):

    """Checks for configuration consistency for settings related to components
    1. Requested components in rose-suite.conf must exist in remap-pp-component's app config
    2. Regridded history files specified in remap-pp-component's config must also exist in regrid-xy's config,
       and the label must be consistent
    """

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # Read the Rose app configuration specified by config_key

        # Read the remap-pp-components and regrid-xy app configs, and report any errors.
        # collect info in these vars
        # set of all available components, to compare to the requests in rose-suite.conf
        available_comps = set()
        # set of all history files, for each component (dict of sets)
        history_files_by_comp = {}
        # regridded label for each component
        regrid_label_by_comp = {}

        # The keys in the Rose app config are the component, with optional ".suffix".
        regex_pp_comp = re.compile('^\w+')

        # first, go through the remap-pp-components config
        path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/remap-pp-components/rose-app.conf'
        node = metomi.rose.config.load(path_to_conf)

        for keys, sub_node in node.walk():
            # only target the keys
            if len(keys) != 1:
                continue
            # skip env and command keys
            item = keys[0]
            if item == "env" or item == "command":
                continue
            comp = regex_pp_comp.match(item).group()

            # add the component to the available-component set
            available_comps.add(comp)

            # add history file to the component dict
            if comp not in history_files_by_comp:
                history_files_by_comp[comp] = set()
            for source in node.get_value([item, 'sources']).split():
                history_files_by_comp[comp].add(source)

            # add regridded label for regridded components
            if node.get_value([item, 'grid']) != "native":
                regrid_label_by_comp[comp] = node.get_value([item, 'grid'])

        #print(available_comps)
        #print(history_files_by_comp)
        #print(regrid_label_by_comp)

        # Requested components (PP_COMPONENTS) in rose-suite.conf must exist in remap-pp-component's app config
        # If they don't, add suitable errors
        requested_comps_str = config.get_value(['template variables', 'PP_COMPONENTS'])
        if requested_comps_str is None:
            self.add_report("template variables", "PP_COMPONENTS", requested_comps_str, "Required and not set")
            return self.reports
        if requested_comps_str == "":
            self.add_report("template variables", "PP_COMPONENTS", requested_comps_str, "Required and not set")
            return self.reports

        requested_comps = requested_comps_str.strip('"').split(' ')
        for comp in requested_comps:
            if comp in available_comps:
                pass
            else:
                self.add_report("template variables", "PP_COMPONENTS", config.get_value(['template variables', 'PP_COMPONENTS']).strip('"'), f"Requested component '{comp}' is not defined in {path_to_conf}")

        # Regridded history files specified in remap-pp-component's config must also exist in regrid-xy's config,
        # and the label must be consistent
        # Record each component's history file prerequisites
        # Verify that each regridded component's history file has compatible regridding config
        path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../app/regrid-xy/rose-app.conf'
        node = metomi.rose.config.load(path_to_conf)
        for comp in requested_comps:
            # skip if not a regridded component
            if comp not in regrid_label_by_comp:
                continue

            # for each regridded history file, check that its regrid label is consistent between the
            # remap-pp-component and regrid-xy configs
            for history_file in history_files_by_comp[comp]:
                success_flag = False
                # examine regrid-xy/rose-app.conf to confirm that this history file has the right regridding instructions
                for keys, sub_node in node.walk():
                    if len(keys) != 1:
                        continue
                    item = keys[0]
                    if item == "env" or item == "command":
                        continue
                    sources = node.get_value([item, 'sources']).split()
                    if history_file in sources:
                        output_grid_type = node.get_value([item, 'outputGridType'])
                        if output_grid_type is None:
                            pass
                        elif "regrid-xy/" + output_grid_type == regrid_label_by_comp[comp]:
                            success_flag = True
                if not success_flag:
                    self.add_report("template variables", "PP_COMPONENTS", config.get_value(['template variables', 'PP_COMPONENTS']).strip('"'), f"Requested component '{comp}' uses history file '{history_file}' with regridding label '{regrid_label_by_comp[comp]}', but this was not found in app/regrid-xy/rose-app.conf")

        return self.reports
