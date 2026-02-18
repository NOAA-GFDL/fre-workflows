# plugins must be properly installed, in-place PYTHONPATH meddling will not work.

from setuptools import setup

## Register plugin
setup(
    name='hello-world',
    version='1.0',
    py_modules=['hello_world'], #name of file
    entry_points={
        # group name: ["plugin_name = module:function"]
        'cylc.pre_configure': [
            'hw = install_plugin.hello_world:pre_configure'
        ],
    }
)

