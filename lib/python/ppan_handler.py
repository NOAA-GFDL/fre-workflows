'''
a custom-made job_runner_handler, named SLURMHandler 
it's specifically for working with cylc, and GFDL's PPAN/slurm
'''

from pathlib import Path
from subprocess import DEVNULL
import shlex
from typing import Tuple

from cylc.flow.job_runner_handlers.slurm import SLURMHandler
from cylc.flow.cylc_subproc import procopen


class PPANHandler(SLURMHandler):
    '''
    major differences from inherited SLURMHandler class:
    1) class method for submit() is defined- it has enough flexibility to
    allow us to parse the job script the way we want.
    2) SUBMIT_CMD_TMPL set to None- this is to prevent
    cylc/flow/job_runner_mgr.py from trying to use it in lieu of the submit()
    class method.

    of slightly less note, methods test_import and test_tool_ops_import are
    for assessing import functionality via pytest, in the tests/dir
    '''

    # job_runner_mgr will never use SLURMHandler's SUBMIT_CMD_TMPL
    # once it realizes that a proper submit() classmethod exists.
    # set to None, just in case.
    SUBMIT_CMD_TMPL = None

    # internal canary/coal mine function for tests
    @classmethod
    def test_import(cls) -> int:
        return 0

    # internal canary/coal mine test for tests
    @classmethod
    def test_tool_ops_import(cls) -> int:
        from .tool_ops_w_papiex import test_import
        return test_import()

    # for submitting a job to SLURM via subprocess call
    @classmethod
    def submit(cls,
               job_file_path: str,
               submit_opts: dict,
               dry_run: bool = False,
               tool_ops: bool = True )  -> Tuple[int, str, str]:
        """
        Submit a job.

        Submit a job and return an instance of the Popen object for the
        submission. This handler inherits from SLURMHandler, and is
        catered to GFDL's PP/AN compute resource.

        SLURMHandler has no real submit command- just SUBMIT_CMD_TMPL.
        this class member is set to None and a submit method defined
        instead. as the SUBMIT_CMD_TMPL approach is locked up within
        the cylc code base.

        when job_runner_mgr._jobs_submit_impl finds PPANHandler.submit()
        via hasattr() or getattr(), it will be used. if it were not, it
        would default to using SUBMIT_CMD_TMPL to form a shell command,
        which is then issued via procopen in cylc/flow/cylc_subproc.py.

        based heavily lines 717 - 738 in cylc/flow/job_runner_mgr.py
        see github.com/cylc/cylc-flow, tag 8.2.1

        You must pass "env=submit_opts.get('env')" to Popen - see
        :py:mod:`cylc.flow.job_runner_handlers.background`
        for an example.

        Args:
            job_file_path: The job file for this submission.
            submit_opts: Job submission options.
            tool_ops: parse created job scripts to add in tags for
                      scraping data via PAPIEX/EPMT
            dry_run: don't actually submit any jobs.

        Returns:
            (ret_code, out, err)
        """

        # choices here identitcal to those in ._jobs_submit_impl
        # when SUBMIT_CMD_TMPL exists instead of submit(). the
        # choices are security-minded,
        proc_stdin_arg = None
        proc_stdin_value = DEVNULL

        # strongly recommended to not add too many things to either err
        # or out. both are parsed to help confirm successful submission
        # to SLURM. if the regex search fails, the submission will
        # incorrectly be pegged as unsuccessful, and the submit retry
        # delay will begin ticking down.
        # if adding to either, end with newline.
        out = ''
        err = ''
        ret_code = 1

        # check that we have a non-empty env dictionary
        env = submit_opts.get('env')
        if dry_run:
            env = None
        elif env is None:
            err = "(ppan_handler) error, submit_opts.get('env') returned None.\n"
            return (1, out, err)

        # set command template according to dry_run
        if dry_run:
            #cmd_tmpl = "sleep 5s"
            cmd_tmpl = "echo HELLO"
        else:
            cmd_tmpl = "sbatch '%(job)s'"

        #----------------------
        if tool_ops:
            try:
                if any([ 'lib.python.' in __name__ ,
                         'tests.test_' in __name__  ]) :
                    out = '(ppan_handler) attempting RELATIVE import from .tool_ops_w_papiex ...\n'
                    from .tool_ops_w_papiex import tool_ops_w_papiex
                else:
                    out = '(ppan_handler) attempting import from tool_ops_w_papiex ...\n'
                    from tool_ops_w_papiex import tool_ops_w_papiex

            except Exception as exc:
                err = f'(ppan_handler) ERROR tool_ops_w_papiex import issue. name={__name__}\n ' + \
                      'exc is: ' + str(exc)
                return (1, out, err)

            try:
                tool_ops_w_papiex(fin_name=job_file_path)

            except Exception as exc:
                err = '(ppan_handler) ERROR papiex ops tooler did not work.\n exc is: ' + str(exc)
                return (1, out, err)

            # this should be handled inside tool_ops_w_papiex TODO
            Path(job_file_path).rename(job_file_path+'.notags') #move job to job.notags
            Path(job_file_path+'.tags').rename(job_file_path) #move job.tags to job
            Path(job_file_path).chmod(0o755) #give the script execute permissions.
            try:
                assert all( [ Path(job_file_path).exists(),
                              Path(job_file_path+'.notags').exists() ] )
            except Exception as exc:
                err = '(ppan_handler) ERROR one of the job files does not exist.\n exc is: ' + \
                      str(exc)
                return (1, out, err)
        #----------------------

        # this helps prevent code-injection attacks. shlex won't parse ';'
        # nor other chars for issuing multiple commands
        command = shlex.split(
            cmd_tmpl % {"job": job_file_path})

        # try submitting the job.
        try:
            cwd = Path('~').expanduser()
            proc = procopen(
                command,
                stdin = proc_stdin_arg,
                stdoutpipe = True,
                stderrpipe = True,
                env = env,
                cwd = cwd
            )
        except OSError as exc:
            # subprocess.Popen has a bad habit of not setting the
            # filename of the executable when it raises an OSError.
            if not exc.filename:
                exc.filename = command[0]
            err = '(ppan_handler) OSError thrown, procopen call.\n exc is: ' + str(exc)
            return (1, out, err)

        # grab return code, stdout, stderr from proc
        try:
            out, err = (
                f.decode() for f in proc.communicate(proc_stdin_value) )
            ret_code = proc.wait()
        except OSError as exc:
            err = 'problem getting output from job-submission proc.\n exc is: ' + str(exc)
            ret_code = 1

        return (ret_code, out, err)

# doc source for approach
#https://cylc.github.io/cylc-doc/stable/html/plugins/job-runners/index.html
JOB_RUNNER_HANDLER = PPANHandler()
