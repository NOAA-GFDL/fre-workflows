#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class GridConsistencyChecker(metomi.rose.macro.MacroBase):
    """History files mapped to a component must be on the same grid."""

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        # rose app config headers are the component name, with optional ".suffix".
        regex_pp_comp = re.compile('^\w+')

        # First, loop over the components and record the grid types for each.
        comp_grids = {}

        for keys, sub_node in config.walk():
            # only target the keys
            if len(keys) != 1:
                continue
            # skip env and command keys
            item = keys[0]
            if item == "env" or item == "command":
                continue

            comp = regex_pp_comp.match(item).group()

            # grid must be set
            grid = config.get_value([item, 'grid'])
            if not grid:
                self.add_report(item, 'grid', None, f"Component item '{comp}' is missing required 'grid' option")

            # record the component's grid
            if comp not in comp_grids:
                comp_grids[comp] = set()
            comp_grids[comp].add(grid)

        # Then loop over again, and report problems if the component has more than one grid type
        for keys, sub_node in config.walk():
            # only target the keys
            if len(keys) != 1:
                continue
            # skip env and command keys
            item = keys[0]
            if item == "env" or item == "command":
                continue

            # record problem if two or more grids are mapped to one component
            comp = regex_pp_comp.match(item).group()
            if len(comp_grids[comp]) >= 2:
                self.add_report(item, 'grid', config.get_value([item, 'grid']), f"Component item '{comp}' has multiple input grid types, which is strongly discouraged.")

        return self.reports
