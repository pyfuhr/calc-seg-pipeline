import os, sys
import hashlib, time

def compute_file_sha1(fname):
    BUF_SIZE = 4096
    sha1 = hashlib.sha1()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def create_metaline(fname):
    sha1hash = compute_file_sha1(fname)
    return f'{fname}, modify_time: {os.path.getmtime(fname)}, sha1:{sha1hash}\n'

def create_meta(main_name, files, comment):
    ret = '--- PyFuhr meta file ---\n'
    ret += comment + '\n'
    for file in files:
        ret += create_metaline(file)
    ret += str(time.ctime()) + '\n'
    ret += '--- End of meta file ---'
    with open(main_name+'.meta', 'w') as f:
        f.write(ret)
    return ret