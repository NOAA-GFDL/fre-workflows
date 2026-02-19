# plugins must be properly installed, in-place PYTHONPATH meddling will not work.

from setuptools import setup, find_packages

## Register plugin
setup(
    name='hello-world',
    version='1.0',
    #py_modules=['install_plugin'], #name of file
    packages=find_packages(),
    entry_points={
        ## Register plugin with cylc
        # plugin type: ["plugin_name = module:function"]
        'cylc.pre_configure': [
            'hw=install_plugin.hello_world:pre_configure'
        ]
    }
)

