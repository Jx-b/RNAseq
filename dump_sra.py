#!/usr/bin/env python3
# This script converts sra files to fastq format using fasterq-dump and performs QC using fastQC

#imports
import os, sys, shlex
from argparse import ArgumentParser
import subprocess as sp

## parse arguments and check folder exists
parser = ArgumentParser()
parser.add_argument("-s" ,"--sradir", dest="sradir",
                    help="Directory containing SRA files", metavar="DIR", type=str)
parser.add_argument("-o", "--outdir", dest="outdir",
                    help="Output directory to store fastq files", metavar="DIR", type=str)
args = parser.parse_args()

SRADIR = vars(args)['sradir']
OUTDIR = vars(args)['outdir']

if SRADIR is None:
    print("You must provide an input directory containing sra files")
    sys.exit()
elif not os.path.isdir(SRADIR):
    print("input folder {} not found".format(SRADIR))
    sys.exit()
    
if OUTDIR is None:
    OUTDIR = 'fastq/'

try:
    os.makedirs(OUTDIR)
except FileExistsError:
    # directory already exists
    pass

# find sra files and check there is at least one
sra_files = [f for f in os.listdir(SRADIR) if f.endswith('.sra')]
if len(sra_files) == 0:
    print("No .sra files found")
    sys.exit()


#helper function to run shell commands
def run_command(command):
    try:
        process = sp.Popen(shlex.split(command), stdout = sp.PIPE, stderr = sp.STDOUT, shell = False)
        idx=0
        for line in process.stdout:
            print(idx, line.decode("UTF-8").replace('\n',''))
    except sp.CalledProcessError as e:
        raise Exception("Error running", command, e.output)
    except FileNotFoundError:
        print("command not found")

########## Step 1: Dump ##########
print("Starting Dump")
for file in sra_files:
    filename = os.path.join(SRADIR, file)
    print('dumping', filename)
    run_command("fasterq-dump --outdir {} {} -e4".format(OUTDIR, filename))
    
    
########## Step 2: QC ##########
print("Starting QC analysis")

try:
    os.makedirs('data/fastqc_output')
except FileExistsError:
    # directory already exists
    pass

fastq_files = [f for f in os.listdir(OUTDIR) if f.endswith('.fastq')]
for fastq in fastq_files:
    filename = os.path.join(OUTDIR,fastq)
    run_command("fastqc {} --outdir data/fastqc_output".format(filename))
