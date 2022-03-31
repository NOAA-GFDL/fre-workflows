#!/home/oar.gfdl.sw/conda/miniconda3/envs/cylc/bin/python
import argparse
import re
import sys
import subprocess
import xml.etree.ElementTree as ET
import metomi.rose.config
import metomi.isodatetime.parsers

#
# Usage: fre-bronx-to-canopy -x XML -e EXP -p PLATFORM -t TARGET
#
# Will overwrite 3 files:
# - rose-suite.conf
# - app/remap-pp-components/rose-app.conf
# - app/regrid-xy/rose-app.conf
#

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
        'hourly': 'PT1H',
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

def main(args):
    xml = args.xml
    expname = args.experiment
    platform = args.platform
    target = args.target

    # input
    tree = ET.parse(xml)
    root = tree.getroot()

    # output
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')
    rose_regrid_xy = metomi.rose.config.ConfigNode()
    rose_regrid_xy.set(keys=['command', 'default'], value='regrid-xy')
    rose_suite = metomi.rose.config.ConfigNode()
    rose_suite.set(keys=['template variables', 'PTMP_DIR'], value="'/xtmp/$USER/ptmp'")
    rose_suite.set(keys=['template variables', 'CLEAN_WORK'], value='True')
    rose_suite.set(keys=['template variables', 'DO_MDTF'], value='False')
    rose_suite.set(keys=['template variables', 'PP_START'], value="'YYYY'")
    rose_suite.set(keys=['template variables', 'PP_STOP'], value="'YYYY'")

    regex_fre_property = re.compile('\$\((\w+)')
    all_components = set()

    print("Running frelist for historyDir/ppDir/gridSpec...")
    print("If this fails, try running the 'frelist' call manually. Did you module load FRE?\n")
    cmd = "frelist -x {} -p {} -t {} {} -d archive".format(xml, platform, target, expname)
    print(">>", cmd)
    process = subprocess.run(cmd, shell=True, check=True, capture_output=True, universal_newlines=True)
    historyDir = process.stdout.strip() + '/history'
    print(historyDir)
    cmd = "frelist -x {} -p {} -t {} {} -d postProcess".format(xml, platform, target, expname)
    print(">>", cmd)
    process = subprocess.run(cmd, shell=True, check=True, capture_output=True, universal_newlines=True)
    ppDir = process.stdout.strip()
    print(ppDir)
    cmd = "frelist -x {} -p {} -t {} {} --evaluate '{}'".format(xml, platform, target, expname, 'input/dataFile[@label="gridSpec"]')
    print(">>", cmd)
    process = subprocess.run(cmd, shell=True, check=True, capture_output=True, universal_newlines=True)
    gridSpec = process.stdout.strip()
    print(gridSpec)
    rose_suite.set(keys=['template variables', 'HISTORY_DIR'], value="'{}'".format(historyDir))
    rose_suite.set(keys=['template variables', 'PP_DIR'], value="'{}'".format(ppDir))

    # read XML
    count_components = 0
    print("\nReading XML...\n")
    for exp in root.iter('experiment'):
        if exp.get('name') == expname:
            #print("DEBUG:", exp)
            segment_node = exp.find('runtime/production/segment')
            segment_time = segment_node.get('simTime')
            segment_units = segment_node.get('units')
            if segment_units == 'years':
                segment = 'P' + segment_time + 'Y'
            elif segment_units == 'months':
                segment = 'P' + segment_time + 'M'
            else:
                raise Exception("Unknown segment units:", segment_units)
            rose_suite.set(keys=['template variables', 'HISTORY_SEGMENT'], value="'{}'".format(segment))

            pp = exp.find('postProcess')
            #print("DEBUG:", pp)
            for comp in exp.iter('component'):
                count_components += 1
                #print("DEBUG:", comp)
                type = comp.get('type')
                all_components.add(type)
                #print("Component", type)
                i = 1
                if comp.get('xyInterp'):
                    grid = "regrid-xy"
                else:
                    grid = "native"
                comp_source = comp.get('source')
                #print("DEBUG, comp source is:", comp_source)
                sources = set()
                for ts in comp.iter('timeSeries'):
                    #print("  Timeseries", i)
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
                        print("WARNING: Skipping a timeSeries with no source and no component source for", type)
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
                    #print("  Regridded")
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
                    rose_regrid_xy.set(keys=[type, 'gridSpec'], value=gridSpec)

    rose_suite.set(keys=['template variables', 'PP_COMPONENTS'], value="'{}'".format(' '.join(sorted(all_components))))

    if count_components:
        print("PP components:", count_components)
    else:
        print("ERROR: No postprocess components found")
        print("Probably, your XML uses xincludes which are not handled by this script currently.")
        print("As a workaround, use the xmllint tool with the --xinclude option to rewrite the XML; e.g.")
        print("    xmllint --xinclude {} > expanded.xml".format(xml))
        exit(1)

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


    print("\nSetting PP chunks...")
    all_chunks = set()
    def duration_to_seconds(duration):
        dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
        return dur.get_seconds()

    for keys, sub_node in rose_remap.walk():
        if len(keys) != 1:
            continue
        item = keys[0]
        if item == "env" or item == "command":
            continue
        chunk = rose_remap.get_value(keys=[item, 'chunk'])
        if chunk == 'P0Y':
            continue
        all_chunks.add(chunk)

    sorted_chunks = list(all_chunks)
    sorted_chunks.sort(key=duration_to_seconds, reverse=False)

    print("  Chunks found:", ', '.join(sorted_chunks))
    assert len(sorted_chunks) >= 2
    rose_suite.set(['template variables', 'PP_CHUNK_A'], "'{}'".format(sorted_chunks[0]))
    rose_suite.set(['template variables', 'PP_CHUNK_B'], "'{}'".format(sorted_chunks[1]))
    print("  Chunks used: ", ', '.join(sorted_chunks[0:2]))
    

    print("\nWriting output files...")
    dumper = metomi.rose.config.ConfigDumper()
    
    outfile = "rose-suite.conf"
    print("  ", outfile)
    dumper(rose_suite, outfile)

    outfile = "app/remap-pp-components/rose-app.conf"
    print("  ", outfile)
    dumper(rose_remap, outfile)

    outfile = "app/regrid-xy/rose-app.conf"
    print("  ", outfile)
    dumper(rose_regrid_xy, outfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FRE Bronx-to-Canopy converter")
    parser.add_argument('--xml', '-x', required=True, help="Bronx XML")
    parser.add_argument('--platform', '-p', required=True, help="Platform")
    parser.add_argument('--target', '-t', required=True, help="Target")
    parser.add_argument('--experiment', '-e', required=True, help="Experiment")
    args = parser.parse_args()
    main(args)
