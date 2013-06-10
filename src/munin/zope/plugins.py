from gocept.munin.client import SimpleMultiGraph, main, SimpleGraph
from munin.zope.memory import vmkeys
from os.path import isdir, basename, abspath, normpath, join, exists
from os import environ, getcwd, symlink
from inspect import isclass
from socket import gethostname
from sys import argv
import urllib


class zodbactivity(SimpleMultiGraph):
    keys = ['total_load_count', 'total_store_count', 'total_connections']
    names = ['Total_objects_loaded', 'Total_objects_stored',
             'Total_connections']
    title = 'ZODB Activity'
    category = 'Zope'
    vlabel = "no"


class zopecache(SimpleMultiGraph):
    keys = ['total_objs', 'total_objs_memory', 'target_number']
    names = ['Total_objects_in_database', 'Total_objects_in_all_caches',
             'Target_number_to_cache']
    title = 'Zope cache parameters'
    category = 'Zope'
    vlabel = "no"


class zopethreads(SimpleMultiGraph):
    keys = ['total_threads', 'free_threads']
    names = ['Total_threads', 'Free_threads']
    title = 'Z2Server threads'
    category = 'Zope'
    vlabel = "no"


keys = vmkeys()


class zopememory(SimpleMultiGraph):
    keys = keys
    names = keys
    title = 'Zope memory usage'
    category = 'Zope'
    vlabel = "no"


class zodbblobsize(SimpleGraph):
    key = name = 'blobsize' 
    title = 'Size of Blobstorage'
    category = 'Zope'
    
    #XXX munin.zope: add support for custom vlabel and cdef similar to Products.ZNagios.munin_client
    cdef = '%s,1048576,/'
    vlabel = 'Size in MB'
    
    
def install(script, cmd, path, prefix=None, suffix=None):
    """ set up plugin symlinks using the given prexix/suffix or the
        current hostname and directory """
    assert isdir(path), 'please specify an existing directory'
    if prefix is None:
        prefix = gethostname()
    if suffix is None:
        suffix = basename(getcwd())
    source = abspath(script)
    for name, value in globals().items():
        if isclass(value) and value.__module__ == __name__:
            plugin = '_'.join((prefix, name, suffix))
            target = normpath(join(path, plugin))
            if not exists(target):
                symlink(source, target)
                print 'installed symlink %s' % target
            else:
                print 'skipped existing %s' % target


def run(ip_address='localhost', http_address=8080, port_base=0, user=None,
        secret = None):
    if 3 <= len(argv) <= 5 and argv[1] == 'install':
        return install(*argv)
    
    port = int(http_address) + int(port_base)
    host = '%s:%d' % (ip_address, port)
    base_url = 'http://%s/@@munin.zope.plugins/%%s' % host
    params = {}
    
    prefix, plugin, suffix = basename(argv[0]).split('_')
    if plugin in ['zodbblobsize']:
        if '-' in suffix:
            params.update(filestorage = suffix.split('-')[1])
#        else:
#            # to enable this, the graphs would need to declare all keys with suffixes
#            params.update(filestorage = '*')
    if secret is not None:
        params.update(secret=secret)
    
    url = base_url
    if params:
        url = base_url + '?' + urllib.urlencode(params).replace('%', '%%')
        
    if not 'URL' in environ:
        environ['URL'] = url
    if not 'AUTH' in environ and user is not None:
        environ['AUTH'] = user
    main()
