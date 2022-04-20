#!/home/oar.gfdl.sw/conda/miniconda3/envs/cylc/bin/python
import argparse
import re
import sys
import subprocess
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

def frelist_xpath(args, xpath):
    cmd = "frelist -x {} -p {} -t {} {} --evaluate '{}'".format(args.xml, args.platform, args.target, args.experiment, xpath)
    print(">>", xpath)
    process = subprocess.run(cmd, shell=True, check=True, capture_output=True, universal_newlines=True)
    result = process.stdout.strip()
    print(result)
    return(result)

def main(args):
    xml = args.xml
    expname = args.experiment
    platform = args.platform
    target = args.target
    debug = args.debug

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

    print("Running frelist for XML parsing...")
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
    gridSpec = frelist_xpath(args, 'input/dataFile[@label="gridSpec"]')
    simTime = frelist_xpath(args, 'runtime/production/@simTime')
    rose_suite.set(keys=['template variables', 'HISTORY_DIR'], value="'{}'".format(historyDir))
    rose_suite.set(keys=['template variables', 'PP_DIR'], value="'{}'".format(ppDir))

    comps = frelist_xpath(args, 'postProcess/component/@type').split()
    rose_suite.set(keys=['template variables', 'PP_COMPONENTS'], value="'{}'".format(' '.join(comps)))

    segment_time = frelist_xpath(args, 'runtime/production/segment/@simTime')
    segment_units = frelist_xpath(args, 'runtime/production/segment/@units')
    if segment_units == 'years':
        segment = 'P' + segment_time + 'Y'
    elif segment_units == 'months':
        segment = 'P' + segment_time + 'M'
    else:
        raise Exception("Unknown segment units:", segment_units)
    rose_suite.set(keys=['template variables', 'HISTORY_SEGMENT'], value="'{}'".format(segment))

    for comp in comps:
        comp_source = frelist_xpath(args, 'postProcess/component[@type="{}"]/@source'.format(comp))
        xyInterp = frelist_xpath(args, 'postProcess/component[@type="{}"]/@xyInterp'.format(comp))
        sourceGrid = frelist_xpath(args, 'postProcess/component[@type="{}"]/@sourceGrid'.format(comp))
        if xyInterp:
            grid = "regrid-xy"
        else:
            grid = "native"
        sources = set()
        timeseries_count = 0

        results = frelist_xpath(args, 'postProcess/component[@type="{}"]/timeSeries[@source]/@*'.format(comp)).split()
        assert len(results) % 3 == 0
        for x in range(0, len(results) // 3):
            x += 1
            label = comp + '.' + str(x)
            source = results[1]
            sources.add(source)
            rose_remap.set(keys=[label, 'source'], value=source)
            freq = results[0]
            rose_remap.set(keys=[label, 'freq'], value=freq)
            chunk = results[2]
            rose_remap.set(keys=[label, 'chunk'], value=chunk)
            rose_remap.set(keys=[label, 'grid'], value=grid)

        results = frelist_xpath(args, 'postProcess/component[@type="{}"]/timeSeries[not(@source)]/@*'.format(comp)).split()
        assert len(results) % 2 == 0
        for x in range(0, len(results) // 2):
            if not comp_source:
                print("WARNING: Skipping a timeSeries with no source and no component source for", comp)
                continue
            x += 1
            label = comp + '.' + str(x)
            sources.add(comp_source)
            rose_remap.set(keys=[label, 'source'], value=comp_source)
            freq = results[0]
            rose_remap.set(keys=[label, 'freq'], value=freq)
            chunk = results[1]
            rose_remap.set(keys=[label, 'chunk'], value=chunk)
            rose_remap.set(keys=[label, 'grid'], value=grid)

        rose_remap.set(keys=[comp + '.static', 'source'], value=' '.join(sources))
        rose_remap.set(keys=[comp + '.static', 'chunk'], value="P0Y")
        rose_remap.set(keys=[comp + '.static', 'freq'], value="P0Y")
        rose_remap.set(keys=[comp + '.static', 'grid'], value=grid)

        if grid == "native":
            continue
        else:
            rose_regrid_xy.set(keys=[comp, 'sources'], value=' '.join(sources))
            sourcegrid_split = sourceGrid.split('-')
            rose_regrid_xy.set(keys=[comp, 'inputGrid'], value=sourcegrid_split[1])
            rose_regrid_xy.set(keys=[comp, 'inputRealm'], value=sourcegrid_split[0])
            interp_split = xyInterp.split(',')
            rose_regrid_xy.set(keys=[comp, 'outputGridLon'], value=interp_split[1])
            rose_regrid_xy.set(keys=[comp, 'outputGridLat'], value=interp_split[0])
            rose_regrid_xy.set(keys=[comp, 'gridSpec'], value=gridSpec)

    if len(comps) > 0:
        print("PP components:", len(comps))
    else:
        print("ERROR: No postprocess components found")
        exit(1)

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

    if len(all_chunks) == 1:
        print("WARNING: Only one chunk found; setting CHUNK_B to 10 years as a crude workaround for now")
        all_chunks.add('P10Y')
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
    parser.add_argument('--debug', action='store_true', required=False, help="print additional output")
    args = parser.parse_args()
    main(args)
