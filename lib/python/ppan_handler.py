#!/app/conda/miniconda/envs/cylc/bin/python

#import sys
#for path in sys.path: print(f'sys.path entry: {path}')

import pathlib
from pathlib import Path
from subprocess import DEVNULL

from typing import (
    Iterable,
    List,
    Tuple,
    TYPE_CHECKING,
)
import shlex

from cylc.flow.job_runner_handlers.slurm import SLURMHandler
from cylc.flow.cylc_subproc import procopen


class PPANHandler(SLURMHandler):

    # set this to None- we want to take the approach used by job_runner_mgr
    # when this is not None, and then stick that flow-control into submit()
    SUBMIT_CMD_TMPL = None

    # internal canary/coal mine test
    @classmethod
    def test_import(cls) -> int:
        return 0

    # internal canary/coal mine test for ops tooling
    @classmethod
    def test_tool_ops_import(cls) -> int:
        import tool_ops_w_papiex
        return tool_ops_w_papiex.test_import()

    # to try to gurantee the text output isn't messed with... for now
    @classmethod
    def filter_submit_output(cls,
                             out: str, err: str) -> Tuple[str, str]:
        return (out, err)

    # the thing I wish would actually work.
    @classmethod
    def submit(cls,
               job_file_path: str,
               submit_opts: dict,
               dry_run=False   )  -> Tuple[int, str, str]:
        """Submit a job.
    
        Submit a job and return an instance of the Popen object for the
        submission. This method is useful if the job submission requires logic
        beyond just running a system or shell command.
    
        See also :py:attr:`ExampleHandler.SUBMIT_CMD_TMPL`.
    
        You must pass "env=submit_opts.get('env')" to Popen - see
        :py:mod:`cylc.flow.job_runner_handlers.background`
        for an example.
    
        Args:
            job_file_path: The job file for this submission.
            submit_opts: Job submission options.
    
        Returns:
            (ret_code, out, err)
    
        """

        
        # the slurm handler has no real submit command- just a SUBMIT_CMD_TMPL
        # when job_runner_mgr.py will check for the submit, and default to using
        # SUBMIT_CMD_TMPL to form a shell command, then issued
        # via procopen in cylc/flow/cylc_subproc.py.
        # so this submit command is essentially going to be what happens there,
        # just wrapped into the submit function. 
        # to start, we copy/pasted lines 717 - 738 in cylc/flow/job_runner_mgr.py
        # below is the version i've landed on currently.
        ret_code = 0
        out = ''
        err = ''

        # canary-in-coalmine output i would like to see everytime.        
        out+='(ppan_handler.py) hello world!\n'

        import tool_ops_w_papiex
        try:
            tool_ops_w_papiex.tool_ops_w_papiex(
                fin_name=job_file_path,
                fms_modulefiles=None)
            out+='(ppan_handler.py) looks like papiex ops tooler finished OK.'
        except:
            err+='(ppan_handler.py) papiex ops tooler did not work.'

        assert all( [ Path(job_file_path).exists(),
                      Path(job_file_path+'.tags').exists() ] )
        job_file_path=job_file_path+'.tags'
        
        if dry_run: out+='(ppan_handler.py) ======= dry_run = True ====== \n'
        out+=f'(ppan_handler.py) arg submit_opts = \n\n{submit_opts}\n\n' #warning, very long.
        out+=f'(ppan_handler.py) arg job_file_path = {job_file_path}\n'

        err+='(ppan_handler.py) hello ERROR world!!!\n'

        env = submit_opts.get('env')
        out+=f'(ppan_handler.py) submit_opts.get(\'env\') = \n {env} \n'
        
        if env is None:
            err+= "(ppan_handler.py) submit_opts.get('env') returned None in lib/python/ppan_handler.py\n"
            return (1, out, err)

        if dry_run:
            cmd_tmpl = "sleep 5s"
        else:
            cmd_tmpl = "sbatch '%(job)s'"
            
        try:
            command = shlex.split(
                cmd_tmpl % {"job": job_file_path})
        except:
            err+=f"(ppan_handler.py) shlex.split(\n    {cmd_tmpl} % {'job':{job_file_path}}\n\n did not work.\n"
            command=shlex.split(
                cmd_tmpl)


        out+='(ppan_handler.py) command is: '
        for part in command:
            out+=f' {part}'
        out+='\n'                

        
        
        proc_stdin_value = DEVNULL
        try:
            cwd = pathlib.Path('~').expanduser()
            out+=f'(ppan_handler.py) cwd={str(cwd)}\n'
            
            proc = procopen(
                command,
                stdin=None,
                stdoutpipe = True,
                stderrpipe = True,
                env = env,
                # paths in directives should be interpreted relative to  $HOME                                                 
                # https://github.com/cylc/cylc-flow/issues/4247         
                cwd = cwd
            )
        except OSError as exc:
            # subprocess.Popen has a bad habit of not setting the       
            # filename of the executable when it raises an OSError.
            out+='\n (ppan_handler.py) !!!!!!!!!!!!!!!!!!!!OSError as exc!!!!!!!!!!!!!!!!!!!!!!\n\n'
            err+='\n (ppan_handler.py) !!!!!!!!!!!!!!!!!!!!OSError as exc!!!!!!!!!!!!!!!!!!!!!!\n\n'
            if not exc.filename:
                exc.filename = command[0]                        
            return 1, out, err

        proc_out, proc_err = (f.decode() for f in proc.communicate(proc_stdin_value))
        out+=f'(ppan_handler.py) procopen output: {proc_out}\n'
        err+=f'(ppan_handler.py) procopen err output: {proc_err}\n'
        try:
            ret_code = proc.wait()
        except:
            err+='(ppan_handler.py) proc.wait() did not work. moving on.'
            ret_code=1

        return (ret_code, out, err)

# based on
#https://cylc.github.io/cylc-doc/stable/html/plugins/job-runners/index.html
JOB_RUNNER_HANDLER = PPANHandler()
