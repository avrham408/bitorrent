import aiofiles
import os
import shutil
import torrent


MODULE_PATH = os.path.dirname(torrent.__path__[0])


def write_to_disc(fd, block_data, seek_position):
    os.lseek(fd, seek_position,os.SEEK_SET)
    os.write(fd, block_data)


def open_file(path):
    # the function return fd
    return os.open(path, os.O_RDWR)
   

def close_file(fd):
    os.close(fd)


def create_file(path, size):
    f = open(path, 'wb')
    f.seek(size - 1)
    f.write(b'\0')
    f.close()


def get_path(*args, base=MODULE_PATH):
    # if you want create_path that not connect to module path just path=False
    if base:
        return os.path.join(base, *args)
    else:
        return os.path.join(*args)


def copy_file(src, dest):
    shutil.copy(src, dest)
