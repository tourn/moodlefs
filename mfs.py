#!/usr/bin/env python

from __future__ import with_statement

import moodlesession

import os
import sys
import errno

import fuse
from fuse import FUSE, FuseOSError, Operations

from BeautifulSoup import BeautifulSoup

class MoodleNode:
    def __init__(self, moodle, name, url):
        self.name = name
        self.moodle = moodle
        self.url = url

class MoodleDir(MoodleNode):
    def __init__(self, moodle, name, url):
        MoodleNode.__init__(self, moodle, name, url)
        self.children = {}

    def find(self, path):
        child, subpath = path.strip('/').split('/',1)

class MoodleFile(MoodleNode):
    def info(self):
        return

    def get(self):
        return


class MoodleFS(Operations):
    def __init__(self):
        print('__init__')
        self.moodle = moodlesession.connect()
        print('connected')
        self.rootURL = 'https://moodle.hsr.ch/course/view.php?id=222'
        #self.root = MoodleDir('#', self.moodle, self.rootURL);

    # Helpers
    # =======

    def _full_path(self, partial):
        raise Error('This method is deprecated')

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        print('access')
        return 0
        if not os.access("/tmp" + path, mode):
                return -errno.EACCES

    def chmod(self, path, mode):
        print('chmod')
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        print('chown')
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        #see man fstat
        dir = 0040555
        file = 0100555
        print('getattr ' + path)
        return { 'st_atime': 0,
                'st_ctime': 0,
                'st_gid': os.getgid(),
                'st_mode': dir, #TODO make dynamic for file/dir
                'st_mtime': 0,
                'st_nlink': 1,
                'st_size': 100, #TODO use http HEAD on files, fluke something on dirs
                'st_uid': os.getuid()
                }
        st = os.lstat('.')
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def readdir(self, path, fh):
        print('readdir ' + path)
        #ignore path for now, just list root
        soup = BeautifulSoup(self.moodle.get(self.rootURL).content)
        dirents = ['.', '..']
        for topic in soup.find('ul', { "class" : "topics" }).contents:
            if topic.has_key('aria-label'):
                dirents.append(topic['aria-label'])
        for r in dirents:
            yield r

    def readlink(self, path):
        print('readlink')
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        print('mknod')
        return os.mknod(self._full_path(path), mode, dev)

    def statfs(self, path):
#        return {
#            'f_namemax': 0,
#            'f_fsid': 0,
#            'f_frsize': 0,
#            'f_bsize': 0,
#            'f_flag': 0
#        }
#        print('statfs')
#        full_path = self._full_path(path)
        stv = os.statvfs('.')
        d = dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
        #print(d)
        return d

    def utimens(self, path, times=None):
        print('utimens')
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        print('open')
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def read(self, path, length, offset, fh):
        print('read')
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def flush(self, path, fh):
        print('flush')
        return os.fsync(fh)

    def release(self, path, fh):
        print('release')
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        print('fsync')
        return self.flush(path, fh)


def main(mountpoint):
    print('main')
    FUSE(MoodleFS(), mountpoint, foreground=True)

if __name__ == '__main__':
    main(sys.argv[1])
