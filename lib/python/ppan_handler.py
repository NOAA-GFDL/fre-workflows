#!/app/conda/miniconda/envs/cylc/bin/python

#import sys
#for path in sys.path: print(f'sys.path entry: {path}')

from pathlib import Path
import shlex
from subprocess import DEVNULL

from cylc.flow.job_runner_handlers.slurm import SLURMHandler
from cylc.flow.cylc_subproc import procopen


class PPANHandler(SLURMHandler):
#class PPANHandler():
    #SUBMIT_CMD_TMPL = "pwd; ls; echo '%(job)s'; sbatch '%(job)s'"
    #SUBMIT_CMD_TMPL = "pwd; ls; echo '%(job)s'; sbatch '%(job)s';"
    #SUBMIT_CMD_TMPL = "pwd; ls; echo '%(job)s'";

    ## this won't work. b.c. shlex?
    #SUBMIT_CMD_TMPL = "pwd; ls"; 
    ## so instead we try... https://docs.python.org/3/library/shlex.html
    #SUBMIT_CMD_TMPL = "pwd {}".format("; ls")

    ### this works!!
    #SUBMIT_CMD_TMPL = "echo 'hello'"

    ### this works!!
    #SUBMIT_CMD_TMPL = "echo '%(job)s'"

    ### this works!!
    #SUBMIT_CMD_TMPL = "cat '%(job)s'"

    ## this works!!
    #SUBMIT_CMD_TMPL = "cat '%(job)s' && echo '%(job)s'"

    ## unsure if this works, but not sure this is the way we should yet. tbh
    ## b.c. the SLURMHandler class has no submit command to take advantage of via super()
    #SUBMIT_CMD_TMPL = None

    @classmethod
    def submit(
            cls,
            job_file_path,
            submit_opts   ): # -> Tuple[int, str, str]:
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
        ret_code = None
        out = None
        err = None

        # canary-in-coalmine output i would like to see everytime.
        out = f'(from ppan_handler.py) hello world!\n'
        out += f'(from ppan_handler.py) arg submit_opts = \n\n{submit_opts}\n\n' #warning, very long.
        out += f'(from ppan_handler.py) arg job_file_path = {job_file_path}\n'

        err = f'(from ppan_handler.py) hello ERROR world!!!\n'

        env = submit_opts.get('env')
        if env is None:
            err += "submit_opts.get('env') returned None in lib/python/ppan_handler.py\n"
            out += err
            return 1, out, err        

        submit_cmd_tmpl = "echo '%(job)s'"
        command = shlex.split(
            submit_cmd_tmpl % {"job": job_file_path})
        out += 'commands are:\n'+' '.join(map(str,command))+'\n'
        proc_stdin_arg = None
        proc_stdin_value = DEVNULL
        
        try:
            ret_code = 0
            #pass
            proc = procopen(
                command,
                stdin      = proc_stdin_arg,
                stdindevnull=None,
                splitcmd = False,
                stdoutpipe = True,
                stderrpipe = True,
                env = env,
                # paths in directives should be interpreted relative to 
                # $HOME                                                 
                # https://github.com/cylc/cylc-flow/issues/4247         
                cwd = Path('~').expanduser()
            )
        except OSError as exc:
            # subprocess.Popen has a bad habit of not setting the       
            # filename of the executable when it raises an OSError.
            out +='\n !!!!!!!!!!!!!!!!!!!!OSError as exc!!!!!!!!!!!!!!!!!!!!!!\n\n'
            if not exc.filename:
                exc.filename = command[0]
            err += '\n'+str(exc)
            #return 1, out, err
            ret_code = 1

        out1, err1 = (f.decode() for f in proc.communicate(proc_stdin_value))
        #ret_code = proc.wait()        
        return ret_code, out, err

# based on
#https://cylc.github.io/cylc-doc/stable/html/plugins/job-runners/index.html
JOB_RUNNER_HANDLER = PPANHandler()



##in terms of she-bangs at the start of this, we have two options:
##### result:
###!/app/conda/miniconda/envs/cylc/bin/python

##### result:
###!/usr/bin/env python3


### result:
#from cylc.flow.job_runner_handlers.slurm import SlurmHandler

## result:
#import cylc
#from cylc import flow.job_runner_handlers.slurm.SlurmHandler as SlurmHandler

## result:
#import cylc
#from cylc import flow.job_runner_handlers.slurm.SlurmHandler


