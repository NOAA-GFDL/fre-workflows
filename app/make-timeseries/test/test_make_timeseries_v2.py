''' for testing fre workflows make-timeseries '''
import pathlib as pl
import pytest
import subprocess
import os
###################################
### Setup
###################################

# Create temporary directories and files to simulate the environment
test_dir = tempfile.TemporaryDirectory()
component = "component"
(Path(test_dir.name) /component).mkdir(parents=True, exist_ok=True)

# Create nested directory structure and files
freq_dir = Path(test_dir.name) / component / 'P1Y'
freq_dir.mkdir(parents=True, exist_ok=True)
(freq_dir / 'test_var.date-01.nc').touch()
(freq_dir / 'test_var.date-02.nc').touch()

output_dir = tempfile.TemporaryDirectory()
###################################
### Tests
###################################

def run_make_timeseries(self, env_vars):
    result = subprocess.run(
        ['./../bin/make_timeseries.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, **env_vars},
        cwd=self.test_dir.name)
    return result



###################################
### Tear down
###################################
# Clean up temporary directories
test_dir.cleanup()
output_dir.cleanup()
