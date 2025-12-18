'''
A custom-made job_runner_handler, named SLURMHandler, that cylc will use to work with GFDL's PPAN/slurm.
Documentation from cylc on this approach is here, but a little thin:
    https://cylc.github.io/cylc-doc/stable/html/plugins/job-runners/index.html

Since the doc does not contain an example this entailed, the codebase of cylc itself was consulted. It is
particularly instructive to read the functions, comments, docstrings etc. within the following files
    cylc/flow/job_runner_mgr.py
    cylc/flow/cylc_subproc.py
    cylc/flow/job_runner_handlers/documentation.py
    cylc/flow/job_runner_handlers/slurm.py
    cylc/flow/job_runner_handlers/background.py
'''

from pathlib import Path
import shlex
from subprocess import DEVNULL
from typing import Tuple

from cylc.flow.job_runner_handlers.slurm import SLURMHandler
from cylc.flow.cylc_subproc import procopen

class PPANHandler(SLURMHandler):
    '''
    major differences from inherited SLURMHandler class within cylc:

      1) class method for submit() is defined- it has enough flexibility to allow us to parse the
         job script the way we want.
      2) SUBMIT_CMD_TMPL set to None- this is to prevent cylc/flow/job_runner_mgr.py from trying to
         use it in lieu of the submit() class method.

    of slightly less note, methods check_import and check_tool_ops_import are for assessing import
    functionality via pytest
    '''

    # job_runner_mgr will never use SLURMHandler's SUBMIT_CMD_TMPL once it realizes that a proper
    # submit() classmethod exists. for explicitness, set to None.
    SUBMIT_CMD_TMPL = None

    @classmethod
    def check_import(cls) -> int:
        '''
        internal canary/coal mine function for tests
        '''
        return 0

    @classmethod
    def check_tool_ops_import(cls) -> int:
        '''
        internal canary/coal mine function for tests
        '''
        from .tool_ops_w_papiex import check_import as check_import_ # pylint: disable=import-outside-toplevel
        return check_import_()

    @classmethod
    def submit(cls,
               job_file_path: str,
               submit_opts: dict,
               dry_run: bool = False,
               tool_ops: bool = True )  -> Tuple[int, str, str]:
        """
        Submit a job and return an instance of the Popen object for the submission. This handler inherits
        from SLURMHandler, and is catered to GFDL's PP/AN compute resource.

        SLURMHandler has no real submit command- just SUBMIT_CMD_TMPL. this class member is set to None
        and a submit method defined instead. as the SUBMIT_CMD_TMPL approach is locked up within the cylc
        code base.

        when job_runner_mgr._jobs_submit_impl finds PPANHandler.submit() via hasattr() or getattr(), it
        will be used. if it were not, it would default to using SUBMIT_CMD_TMPL to form a shell command,
        which is then issued via procopen in cylc/flow/cylc_subproc.py.

        based heavily on lines 717-738 in cylc/flow/job_runner_mgr.py, github.com/cylc/cylc-flow, tag 8.2.1

        You must pass "env = submit_opts.get('env')" to Popen - see the following for example:
            :py:mod:`cylc.flow.job_runner_handlers.background`

        Args:
            job_file_path: The job file for this submission.
            submit_opts: Job submission options.
            tool_ops: parse created job scripts to add in tags for scraping data via PAPIEX/EPMT
            dry_run: don't actually submit any jobs.

        Returns:
            (ret_code, out, err)
        """

        # security-minded choices taken from ._jobs_submit_impl, when SUBMIT_CMD_TMPL exists instead of submit()
        proc_stdin_arg = None
        proc_stdin_value = DEVNULL

        # strongly recommended to not add too many things to either err or out. both are parsed with regex to confirm
        # successful submission to SLURM. if the regex search fails, the submission will be pegged as unsuccessful,
        # and the submit retry delay will begin ticking down.
        # if assigning or adding to either, end with newline.
        out = ''
        err = ''
        ret_code = 1

        out = "(ppan_handler) checking submit_opts dictionary for env.\n"
        env = submit_opts.get('env')
        if env is None and not dry_run: # OK if dry_run = True, for debugging usually
            err = "(ppan_handler) error, submit_opts.get('env') returned None.\n"
            return (1, out, err)

        # set command template, check dry_run accordingly
        cmd_tmpl = "sbatch '%(job)s'"
        if dry_run:
            cmd_tmpl = "echo HELLO"

        if tool_ops:
            try:
                if any([ 'lib.python.' in __name__ ,
                         'tests.test_' in __name__  ]) :
                    out = '(ppan_handler) attempting RELATIVE import from .tool_ops_w_papiex ...\n'
                    from .tool_ops_w_papiex import tool_ops_w_papiex # pylint: disable=import-outside-toplevel
                else:
                    out = '(ppan_handler) attempting import from tool_ops_w_papiex ...\n'
                    from tool_ops_w_papiex import tool_ops_w_papiex # pylint: disable=import-outside-toplevel

            except ImportError as exc:
                err = f'(ppan_handler) ERROR tool_ops_w_papiex import issue. name={__name__}. exc is: {exc}'
                return (1, out, err)

            try:
                out = f"(ppan_handler) attempting to tag ops in {job_file_path}, creating {job_file_path}.tags"
                tool_ops_w_papiex( fin_name = job_file_path )
            except Exception as exc: # pylint: disable=broad-exception-caught
                err = f'(ppan_handler) ERROR papiex ops tooler did not work.\n exc is: {exc}'
                return (1, out, err)

            out = "(ppan_handler) sanity checking that job scripts were created as expected."
            if not all( [ Path( job_file_path ).exists(),
                          Path( f'{job_file_path}.tags' ).exists() ] ):
                err = f'(ppan_handler) ERROR a job file does not exist:\n {job_file_path} \n {job_file_path}.tags'
                return (1, out, err)

            # move job to job.notags
            Path( job_file_path ).rename( f'{job_file_path}.notags' )

            # move job.tags to job, and make it executable
            Path( f'{job_file_path}.tags' ).rename( job_file_path )
            Path( job_file_path ).chmod( 0o755 )

            out = "(ppan_handler) sanity checking that job scripts were renamed as expected."
            if not all( [ Path( job_file_path ).exists(),
                          Path( f'{job_file_path}.notags' ).exists() ] ):
                err = f'(ppan_handler) ERROR a job file does not exist:\n {job_file_path} \n {job_file_path}.notags'
                return (1, out, err)

        # helps prevent code-injection attacks, ';' and other chars for issuing multiple commands won't get parsed
        # if those characters are there, the splitting tends to create a command that errors out because of syntax
        command = shlex.split(
            cmd_tmpl % {"job": job_file_path} )

        try:
            out = "(ppan_handler) attempting job submission."
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
            # subprocess.Popen has a bad habit of not setting the filename of the exception when it raises an OSError
            if not exc.filename:
                exc.filename = command[0]
            err = f'(ppan_handler) OSError thrown, procopen call.\n exc is {exc}'
            return (1, out, err)

        # grab return code, stdout, stderr from proc
        try:
            out = '(ppan_handler) attempting to decode process output.' # if error, out won't be reassigned
            out, err = (
                f.decode() for f in proc.communicate(proc_stdin_value) )
            ret_code = proc.wait()
        except OSError as exc:
            err = f'problem getting output from job-submission proc.\n exc is: {exc}'
            ret_code = 1

        return (ret_code, out, err)

JOB_RUNNER_HANDLER = PPANHandler()
