import tempfile
from netCDF4 import Dataset
import pytest
import os
import data_lineage.bloomfilter.HashGen as hg

NAME = 'test.nc'
DIMENSIONS = {'time' : 10, 'lat' : 180, 'lon' : 288}
HISTORY = f'Thu Jan 01 00:00:00 1900: cdo -O splitmon {NAME}'

@pytest.fixture
def generate_test_netcdf_file(request):
    """
    Generates a test netcdf file. Destroyed after test finishes
    """
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, NAME)

    with (Dataset(test_file, 'w') as ncfile):
        for dim_name in DIMENSIONS:
            size = DIMENSIONS[dim_name]
            ncfile.createDimension(dim_name, size)

        for dim_name in DIMENSIONS:
            var = ncfile.createVariable('var_' + dim_name, 'f8', (dim_name,))

        ncfile.history = HISTORY

    def finalize():
        """
        Removes file after the test is finished using it
        """
        os.remove(test_file)
        os.rmdir(test_dir)

    request.addfinalizer(finalize)

    return test_file


def mock_metadata(file_path):
    """
    Mocks the expected behavior of scrape_metadata
    """
    metadata = ''
    meta_dims = ''
    meta_vars = ''

    # Add dimensions
    for dim_name in DIMENSIONS:
        size = DIMENSIONS[dim_name]
        meta_dims = f'{meta_dims}{dim_name} = {size}\n'
        meta_vars = f"{meta_vars}float64 var_{dim_name}(('{dim_name}',)) ;\n"

    metadata = f'{meta_dims}{meta_vars}{HISTORY}{file_path}'

    return metadata


def test_create_file_hash(generate_test_netcdf_file):
    file_path = generate_test_netcdf_file
    file_hash = hg.main(file_path)

    assert file_hash is not None

def test_scrape_metadata(generate_test_netcdf_file):
    file_path = generate_test_netcdf_file
    expected = mock_metadata(file_path)
    actual = hg.scrape_metadata(file_path)

    assert actual == expected

def test_hash_generation(generate_test_netcdf_file):
    file_path = generate_test_netcdf_file
    metadata = hg.scrape_metadata(file_path)
    hash = hg.generate_hash(metadata)

    assert isinstance(hash, str)
    assert len(hash) > 0
