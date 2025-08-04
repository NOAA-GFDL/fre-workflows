''' for testing fre workflows make-timeseries '''
import unittest
import os
import tempfile
import subprocess
from pathlib import Path

class TestMakeTimeseries(unittest.TestCase):

    ''' Do all settup of temporary test locations as a separate function'''
    def setUp(self):
        # Create temporary directories and files to simulate the environment
        self.test_dir = tempfile.TemporaryDirectory()
        self.component = "component"
        (Path(self.test_dir.name) / self.component).mkdir(parents=True, exist_ok=True)
        
        # Create nested directory structure and files
        self.freq_dir = Path(self.test_dir.name) / self.component / 'P1Y'
        self.freq_dir.mkdir(parents=True, exist_ok=True)
        (self.freq_dir / 'test_var.date-01.nc').touch()
        (self.freq_dir / 'test_var.date-02.nc').touch()

        self.output_dir = tempfile.TemporaryDirectory()


    def run_make_timeseries(self, env_vars):
        result = subprocess.run(
            ['./../bin/make_timeseries'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, **env_vars},
            cwd=self.test_dir.name
        )
        return result

    '''Do all the tear down of temprary files and directories at the end'''
    def tearDown(self):
        # Clean up temporary directories
        self.test_dir.cleanup()
        self.output_dir.cleanup()
