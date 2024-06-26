from setuptools import setup, find_packages

setup(
    name='data_lineage',  # Required: Name of your project
    version='0.1.0',  # Required: Version of your project
    packages=find_packages(),  # Required: Automatically find packages in your project
    install_requires=[],  # Optional: List dependencies here
    python_requires='>=3.9',  # Optional: Specify the Python versions you support
    entry_points={  # Optional: define scripts or executables
        'console_scripts': [
            'generate_hash=data_lineage.bloomfilter.HashGen:start',
            'string_compress=data_lineage.bloomfilter.StringCompression:string_compress',
        ],
    },
)
