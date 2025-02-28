''' This script will parse a yaml and run the nccheck script to validate the number of timesteps '''

import yaml
import click
import re
from fre.pp import nccheck_script as ncc
import os 

levels={}

@click.command()
@click.option('--diag_out','-d', required = True, help = "Diag out file to be parsed")
def validate(diag_out):
    with open(diag_out, 'r') as f:
        diag_out = yaml.safe_load(f)
        path="/home/Ciheim.Brown/testing"
        for x in range(len(diag_out['diag_files'])):
            filename = diag_out['diag_files'][x]['file_name']
            expected_timelevels = diag_out['diag_files'][x]['number_of_timelevels']
            levels.update({str(filename):expected_timelevels})
            #x = re.search(r'\.(.*?)\.', filename)
            #print(x)
            #x = r"\.(.*?)\."
            #print(re.search(x,filename))
            #print(diag_out['diag_files'][x]['number_of_timelevels'])
            #ncc.check(path+filename,2)
        print(levels)
    files = os.listdir(path)
    for _file in files:
        split_filename = re.search(r"\.(.*?)\.",_file)
        if 'diag_manifest' not in str(split_filename):
            result = ncc.check(_file,levels[split_filename])
            if result==1:
                print('good')
            else:
                print('bad')

if __name__ == '__main__':
    validate()
