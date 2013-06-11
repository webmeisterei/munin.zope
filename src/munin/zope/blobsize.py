import os
import sys
from os.path import join, getsize
import time
from plone.memoize import ram

@ram.cache(lambda *args: (time.time() // (60 * 60), args[1]))
def getFolderSize(path):
    """returns size of directory in Bytes

    size is obtained on linux system using du, on other systems 
    by walking through all subdirectories
    
    for performance reasons the result is cached for 1 hour
    """
    if sys.platform.startswith('linux'):
        return _getFolderSizeUsingDU(path)
    
    return _getFolderSizePythonic(path)



def _getFolderSizePythonic(path):
    """returns size of directory in Bytes
    
    leads to same result as `du -b --apparent-size -s`
    since it counts directories with 4096 bytes
    http://stackoverflow.com/questions/4080254/python-os-stat-st-size-gives-different-value-than-du
    """
    file_walker = (
        os.path.join(root, f)
        for root, _, files in os.walk(path)
        for f in files
    )
    dir_walker = (
        4096
        for root, dirs, _ in os.walk(path)
        for d in dirs
    )
    return 4096 + sum(getsize(f) for f in file_walker) + sum(size for size in dir_walker)



def _getFolderSizeUsingDU(path):
    """faster then pythonic way
    http://stackoverflow.com/questions/4080254/python-os-stat-st-size-gives-different-value-than-du
    """
    import commands   
    return int(commands.getoutput('du -bs --apparent-size %s' % path).split()[0])
