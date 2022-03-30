#!/home/oar.gfdl.sw/conda/miniconda3/envs/cylc/bin/python
import re
import sys
import xml.etree.ElementTree as ET
import metomi.rose.config

# Usage: fre-bronx-to-canopy -x XML -E EXP
#
# Will overwrite 3 files:
# - rose-suite.conf
# - app/remap-pp-components/rose-app.conf
# - app/regrid-xy/rose-app.conf

def freq_from_legacy(legacy_freq):
    """Return ISO8601 duration given Bronx-style frequencies

    Arguments:
        legacy_freq (str)
"""
    lookup = {
        'annual': 'P1Y',
        'monthly': 'P1M',
        'seasonal': 'P3M',
        'daily': 'P1D',
        '120hr': 'P120D',
        '12hr': 'PT12H',
        '8hr': 'PT8H',
        '6hr': 'PT6H',
        '4hr': 'PT4H',
        '3hr': 'PT3H',
        '2hr': 'PT2H',
        '1hr': 'PT1H',
        '30min': 'PT30M' }
    return lookup[legacy_freq]

def chunk_from_legacy(legacy_chunk):
    """Return ISO8601 duration given Bronx-style chunk

    Arguments:
        legacy_chunk (str)
"""
    regex = re.compile('(\d+)(\w+)')
    match = regex.match(legacy_chunk)
    assert match
    if match.group(2) == "yr":
        return 'P{}Y'.format(match.group(1))
    elif match.group(2) == 'mo':
        return 'P{}M'.format(match.group(1))
    else:
        raise Exception('Unknown time units', match.group(2))



#xml = '/home/Sergey.Malyshev/ncrc/lm4p2/xanadu/lm4p2-am4p0pi.xml'
#expname = 'lm4p2-am4p0pi'
#xml = '/home/Fanrong.Zeng/ncrc/SPEAR_xml/xml/SPEAR_c192_o1_FA_H+ssp119+245+534OS.30mems.newlayout.bronx-19.xml'
xml = 'expanded.hope.xml'
expname = 'SPEAR_FA_c192_o1_Scen_SSP119_IC2011_K50_ens_01_03'

# input
tree = ET.parse(xml)
root = tree.getroot()

# output
rose_remap = metomi.rose.config.ConfigNode()
rose_remap.set(keys=['command', 'default'], value='remap-pp-components')
rose_regrid_xy = metomi.rose.config.ConfigNode()
rose_regrid_xy.set(keys=['command', 'default'], value='regrid-xy')

rose_suite = metomi.rose.config.ConfigNode()
rose_suite.set(keys=['template variables', 'PTMP_DIR'], value='/xtmp/$USER/ptmp')
rose_suite.set(keys=['template variables', 'CLEAN_WORK'], value='True')
rose_suite.set(keys=['template variables', 'DO_MDTF'], value='False')

regex_fre_property = re.compile('\$\((\w+)')






# read XML
print("Reading XML...\n")
for exp in root.iter('experiment'):
    if exp.get('name') == expname:
        #print("DEBUG:", exp)
        pp = exp.find('postProcess')
        #print("DEBUG:", pp)
        for comp in exp.iter('component'):
            #print("DEBUG:", comp)
            type = comp.get('type')
            print("Component", type)
            i = 1
            if comp.get('xyInterp'):
                grid = "regrid-xy"
            else:
                grid = "native"
            comp_source = comp.get('source')
            #print("DEBUG, comp source is:", comp_source)
            sources = set()
            for ts in comp.iter('timeSeries'):
                print("  Timeseries", i)
                if i == 1:
                    label = type
                    #print("    ", type)
                else:
                    label = type + '.' + str(i)
                    #print("    ", type, i)
                source = ts.get('source')
                if source:
                    s = source
                elif comp_source:
                    s = comp_source
                else:
                    print("WARNING: Skipping a timeSeries with no source and no component source")
                    continue
                #print("    ", s)
                sources.add(s)
                #print("DEBUG:", sources)
                rose_remap.set(keys=[label, 'source'], value=s)
                freq = ts.get('freq')
                #print("    ", freq)
                rose_remap.set(keys=[label, 'freq'], value=freq)
                chunk = ts.get('chunkLength')
                rose_remap.set(keys=[label, 'chunk'], value=chunk)
                rose_remap.set(keys=[label, 'grid'], value=grid)
                #print("    ", chunk)
                #print("    ", grid)
                i = i + 1

            #print("  Statics")
            #print("    ", type, ".static")
            #print("DEBUG", sources)
            #print("    ", ", ".join(sources))
            rose_remap.set(keys=[type + '.static', 'source'], value=' '.join(sources))
            rose_remap.set(keys=[type + '.static', 'chunk'], value="P0Y")
            rose_remap.set(keys=[type + '.static', 'freq'], value="P0Y")
            rose_remap.set(keys=[type + '.static', 'grid'], value=grid)

            if grid == "native":
                #print("  No regridding")
                continue
            else:
                print("  Regridded")
                #print("    ", type)
                #print("    ", ", ".join(sources))
                interp = comp.get('xyInterp')
                #print("    ", interp)
                sourcegrid = comp.get('sourceGrid')
                #print("    ", sourcegrid)
                rose_regrid_xy.set(keys=[type, 'sources'], value=' '.join(sources))
                sourcegrid_split = sourcegrid.split('-')
                rose_regrid_xy.set(keys=[type, 'inputGrid'], value=sourcegrid_split[1])
                rose_regrid_xy.set(keys=[type, 'inputRealm'], value=sourcegrid_split[0])
                interp_split = interp.split(',')
                rose_regrid_xy.set(keys=[type, 'outputGridLon'], value=interp_split[1])
                rose_regrid_xy.set(keys=[type, 'outputGridLat'], value=interp_split[0])





print("\nLooking up FRE properties...")
properties = dict()

for keys, sub_node in rose_remap.walk():
    if len(keys) != 1:
        continue
    item = keys[0]
    if item == "env" or item == "command":
        continue
    value = rose_remap.get_value(keys=[item, 'chunk'])
    match = regex_fre_property.match(value)
    if not match:
        pass
    else:
        name = match.group(1)
        if name in properties:
            pass
        else:
            string = './property[@name="{}"]'.format(name)
            results = root.findall(string)
            assert len(results) == 1
            properties[name] = results[0].get('value')
            print("  {}: {}".format(name, properties[name]))
        rose_remap = rose_remap.set([item, 'chunk'], properties[name])


print("\nConverting Bronx date info to ISO8601...")
freq_from_legacy('annual')

for keys, sub_node in rose_remap.walk():
    if len(keys) != 1:
        continue
    item = keys[0]
    if item == "env" or item == "command":
        continue
    if ".static" in item:
        continue
    freq_legacy = rose_remap.get_value(keys=[item, 'freq'])
    rose_remap.set([item, 'freq'], freq_from_legacy(freq_legacy))
    chunk_legacy = rose_remap.get_value(keys=[item, 'chunk'])
    rose_remap.set([item, 'chunk'], chunk_from_legacy(chunk_legacy))


print("\nWriting output files...")
dumper = metomi.rose.config.ConfigDumper()

outfile = "rose-suite.conf.new"
print("  ", outfile)
dumper(rose_suite, outfile)

outfile = "app/remap-pp-components/rose-app.conf"
print("  ", outfile)
dumper(rose_remap, outfile)

outfile = "app/regrid-xy/rose-app.conf"
print("  ", outfile)
dumper(rose_regrid_xy, outfile)
