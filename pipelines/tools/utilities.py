### Helper functions for the rnaseq pipelines ###

import os, sys
import ftplib, requests, shlex
import subprocess as sp
import tools.progressbar as pg
import IPython.display

N_CPU = os.cpu_count()

def download_file(url, local_filename):
    with open(local_filename, 'wb') as f:
        response = requests.get(url, stream=True)
        filesize = response.headers.get('content-length')
        if filesize is None:
            f.write(response.content)
        else:
            print('*** Downloading {} (size {} MB) ***'.format(local_filename, filesize))
            for chunk in pg.log_progress(response.iter_content(chunk_size=max(int(int(filesize)/1000),1024*1024)),every=1):
                f.write(chunk)
    return local_filename

def download_ftp(ftp, path_to_remote_file, local_name):
    if os.path.exists(local_name):
        print(local_name, 'already downloaded')
    else:
        #open ftp session
        ftp = ftplib.FTP(ftp)
        ftp.login()
        filesize = ftp.size(path_to_remote_file)
        with open(local_name, 'wb') as f:
            print('*** Downloading {} (size {} MB) ***'.format(local_name, filesize))
            p = pg.Progressbar(filesize)
            def callback(chunk):
                f.write(chunk)
                p.update_progress(len(chunk))

            ftp.retrbinary('RETR '+path_to_remote_file, callback, blocksize = max(int(int(filesize)/1000),1024*1024))
        ftp.quit() #close session

def display_link(url):
    raw_html = f'<a href="{url}" target="_blank">{url}</a>'
    return IPython.display.display(IPython.display.HTML(raw_html))

#helper function to run shell commands
def run_command(command):
    try:
        process = sp.Popen(shlex.split(command), stdout = sp.PIPE, stderr = sp.STDOUT, shell = False)
        for line in process.stdout:
            print(line.decode("UTF-8").replace('\n',''))
    except sp.CalledProcessError as e:
        raise Exception("Error running", command, e.output)
    except FileNotFoundError:
        print("command not found")