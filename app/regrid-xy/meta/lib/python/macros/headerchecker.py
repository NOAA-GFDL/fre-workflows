#!/usr/bin/env python
import os
import re
import metomi.rose.macro

class HeaderChecker(metomi.rose.macro.MacroBase):

    """Checks that input grid is correctly set
    """

    def validate(self, config, meta_config=None):
        """Return a list of errors, if any."""

        #path_to_conf = os.path.dirname(os.path.abspath(__file__)) + '/../../../../rose-app.conf'
        #node = metomi.rose.config.load(path_to_conf)

        #Accepted configurations
        grids = {'cubedsphere','tripolar'}
        realms = {'atmos','land','ocean'}
        interp = {'conserve_order1','conserve_order2','bilinear'}
        ignore = {'env','command'}

        #Looping over all headers and checking configurations
        for keys, sub_node in config.walk():

            if len(keys) == 1 and keys[0] not in ignore:
               
                inputGrid = config.get_value([keys[0], 'inputGrid'])
                if inputGrid is None or inputGrid not in grids:
                    if inputGrid is None:
                        self.add_report(keys[0],'inputGrid',inputGrid,"Value required")
                    else:
                        self.add_report(keys[0],'inputGrid',inputGrid,"Not set correctly. Accepted values: cubedsphere,tripolar")

                inputRealm = config.get_value([keys[0], 'inputRealm'])
                if inputRealm is None or inputRealm not in realms:
                    if inputRealm is None:
                        self.add_report(keys[0],'inputRealm',inputRealm,"Value required")
                    else:
                        self.add_report(keys[0],'inputRealm',inputRealm,"Not set correctly. Accepted values: atmos,land,ocean")

                interpMethod = config.get_value([keys[0], 'interpMethod'])
                if interpMethod is None or interpMethod not in interp:
                    if interpMethod is None:
                        self.add_report(keys[0],'interpMethod',interpMethod,"Value required")
                    else:
                        self.add_report(keys[0],'interpMethod',interpMethod,"Not set correctly. Accepted values: conserve_order1,conserve_order2,bilinear")


                outputGridType = config.get_value([keys[0], 'outputGridType'])
                if outputGridType is None or '/' in outputGridType:
                    if outputGridType is None:
                        self.add_report(keys[0],'outputGridType',outputGridType,"Value required")
                    elif '/' in outputGridType:
                        self.add_report(keys[0],'outputGridType',outputGridType,"Remove slash")
                else: 
                    if 'default' in outputGridType:
                        outputGridLat = config.get_value([keys[0], 'outputGridLat'])
                        outputGridLon = config.get_value([keys[0], 'outputGridLon'])
                        if outputGridLat is None:
                            self.add_report(keys[0],'outputGridLat',outputGridLat,"Value required")
                        elif not outputGridLat.isnumeric():
                            self.add_report(keys[0],'outputGridLat',outputGridLat,"Value must be a number")
                        if outputGridLon is None:
                            self.add_report(keys[0],'outputGridLon',outputGridLon,"Value required")
                        elif not outputGridLon.isnumeric():
                            self.add_report(keys[0],'outputGridLon',outputGridLon,"Value must be a number")

                sources = config.get_value([keys[0], 'sources'])
                if sources is None:
                    self.add_report(keys[0],'sources',sources,"Value required")

        return self.reports
