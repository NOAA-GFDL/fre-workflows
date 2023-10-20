#!/app/conda/miniconda/envs/cylc/bin/python

import os
ppan_handler_path=str(os.environ.get('PWD'))+'/lib/python'

import sys
sys.path.append(ppan_handler_path)

test_job_file_path='/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7/log/job/19800101T0000Z/pp-starter/01/job'
test_submit_opts={'execution_time_limit': 14400.0,
                  'env':
                  environ({
                      'MANPATH': ':/opt/puppetlabs/puppet/share/man',
                      'HOSTNAME': 'workflow1.princeton.rdhpcs.noaa.gov',
                      'CYLC_DEBUG': 'true',
                      'ROSE_ORIG_HOST': 'an104.princeton.rdhpcs.noaa.gov',
                      'CYLC_VERSION': '8.2.1',
                      'SHELL': '/bin/bash',
                      'HISTSIZE':'1000',
                      'CYLC_WORKFLOW_RUN_DIR':'/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7',
                      'SSH_CLIENT': '140.208.147.174 46532 22',
                      'PYTHONUNBUFFERED': 'true',
                      'QTDIR': '/usr/lib64/qt-3.3',
                      'QTINC': '/usr/lib64/qt-3.3/include',
                      'LC_ALL': 'en_US.UTF-8',
                      'QT_GRAPHICSSYSTEM_CHECKED': '1',
                      'CYLC_WORKFLOW_INITIAL_CYCLE_POINT': '19800101T0000Z',
                      'USER': 'Ian.Laflotte',
                      'CYLC_WORKFLOW_SHARE_DIR': '/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7/share',
                      'CYLC_WORKFLOW_LOG_DIR': '/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7/log/scheduler',
                      'CYLC_CYCLING_MODE': 'gregorian',
                      'PATH': '/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7/bin:/home/fms/fre-canopy/system-settings/bin:/usr/lib64/qt-3.3/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/opt/puppetlabs/bin:/var/lib/snapd/snap/bin:/home/Ian.Laflotte/bin:/usr/local/slurm/default/bin:/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin:/usr/local/sbin',
                      'MAIL': '/var/spool/mail/Ian.Laflotte',
                      'PWD': '/',
                      'CYLC_WORKFLOW_NAME': 'am5_c96L33_amip',
                      'LANG': 'en_US',
                      'SQUEUE_FORMAT': '%.10i %.70j %.10u %.2t %.10M',
                      'HISTCONTROL': 'ignoredups',
                      'CYLC_WORKFLOW_NAME_BASE': 'am5_c96L33_amip',
                      'CYLC_UTC': 'True',
                      'HOME': '/home/Ian.Laflotte',
                      'SHLVL': '1',
                      'CYLC_WORKFLOW_WORK_DIR': '/home/Ian.Laflotte/cylc-run/am5_c96L33_amip/run7/work',
                      'LOGNAME': 'Ian.Laflotte',
                      'QTLIB': '/usr/lib64/qt-3.3/lib',
                      'CYLC_VERBOSE': 'true',
                      'CYLC_WORKFLOW_FINAL_CYCLE_POINT': '19810101T0000Z',
                      'XDG_DATA_DIRS': '/usr/local/share:/usr/share:/var/lib/snapd/desktop',
                      'SSH_CONNECTION': '140.208.147.174 46532 140.208.147.124 22',
                      'LESSOPEN': '||/usr/bin/lesspipe.sh %s',
                      'ROSE_VERSION': '2.1.0',
                      'LC_TIME': 'C',
                      'CYLC_SITE_CONF_PATH': '/home/fms/fre-canopy/system-settings/bin/..',
                      'CYLC_WORKFLOW_ID': 'am5_c96L33_amip/run7'})}



def test_import():
    from ppan_handler import PPANHandler
    test_handler=PPANHandler()
    
    assert(test_handler.test_import() == 0)

def test_filter_submit_output(): 
    from ppan_handler import PPANHandler
    test_handler=PPANHandler()

    assert(
        test_handler.filter_submit_output('FOO','BAR')
        == ('FOO', 'BAR')
        )
        
   
    
def test_submit():
    from ppan_handler import PPANHandler
    test_handler=PPANHandler()

    job_file_path=''
    submit_opts={'env':{}}
    
    ret_code, ret_out, ret_err = test_handler.submit(job_file_path=job_file_path,
                                          submit_opts=submit_opts,
                                          dry_run=False)
    assert(ret_code == 0)


