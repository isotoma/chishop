#!/usr/bin/env python

from distutils.command.register import register
from distutils.command.upload import upload
from distutils.core import Distribution
import gzip
from os import listdir, chdir, getcwd
from os.path import isdir
from pkginfo import BDist
import tarfile

FIELD_TRANSLATE = {'summary':'description',
                   'home_page':'url'}
DEF_AUTHOR = {'author':'unknown',
              'author_email':'unknown@unknown',}
DEF_FIELDS = {'version':'0.0.1',
              'name':'unknown',
              'url':'http://unknown/'}

class DumbUploader(object):
    '''Uploader for random bdist files'''
    def __init__(self, repository, username, password):
        self.repository = repository
        self.username = username
        self.password = password
        
        self.filename = None
        self.distribution = None
    
    def setDistFile(self,filename):
        self.filename = filename
        try:
            package = BDist(filename)
        except ValueError, e:
            print e
            return False
        
        metadata = dict([(k,getattr(package,k)) for k in package.iterkeys()
                         if getattr(package,k)])
        
        for (inkey,outkey) in FIELD_TRANSLATE.iteritems():
            if getattr(package,inkey,None):
                metadata[outkey] = metadata[inkey]
                del metadata[inkey]
        
        got_a = 'author' in metadata and 'author_email' in metadata
        got_m = 'maintainer' in metadata and 'maintainer_email' in metadata
        if not(got_a or got_m):
            for (k,v) in DEF_AUTHOR.iteritems():
                if k not in metadata:
                    metadata[k] = v
        
        for (k,v) in DEF_FIELDS.iteritems():
            if k not in metadata:
                metadata[k] = v
        
        self.distribution = Distribution(metadata)
        return True
    
    def register(self):
        #python setup.py register -r chishop --show-response
        r = register(self.distribution)
        r.repository = self.repository
        r.run()
        print '%s registered' %(self.filename)
    
    def bdist_dumb(self):
        #python setup.py sdist upload -r http://localhost:8000/ --show-response
        command = 'bdist_dumb'
        
        pyversion = 'any'
        self.distribution.dist_files.append((command,pyversion,self.filename))
        u = upload(self.distribution)
        u.username = self.username
        u.password = self.password
        u.repository = self.repository
        u.run()
        print '%s uploaded' %(self.filename)

def unpack(filename):
    """Check what sort of package we have (tar.gz, zip or egg), unpack it and 
    get it uploaded."""

    if filename.endswith('.tar.gz') or filename.endswith('.zip'):
        print 'tar/zip!'
        decompress(filename)
    elif filename.endswith('.egg'):
        print 'egg!'
    else:
        return False

def decompress(filename):
    """Take either a zip or gz file and decompress it and untar it if needed."""    
    
    if filename.endswith('.gz'):
        print "ungzipping!"
        zipped_handle = gzip.open(filename, 'rb')
        file_contents = zipped_handle.read()
        
        # create a .tar file to decompress into
        tar_filename = filename.rsplit('.', 1)[0]
        if tar_filename:
            output = open(tar_filename, 'wb')
            output.writelines(file_contents)
            output.close()
            zipped_handle.close()
    
            # test we have a tar file
            if tarfile.is_tarfile(tar_filename):
                tar_file = tarfile.open(tar_filename)
                tar_file.extractall()
                tar_file.close()

            else:
                return False
        else:
            return False
    

if __name__ == '__main__':
    from optparse import OptionParser
    from ConfigParser import ConfigParser
    import os.path
    
    def read_rc_file(f,repository):
        '''stolen from distutils.config'''
        if os.path.exists(f):
            config = ConfigParser()
            config.read(f)
            sections = config.sections()
            if 'distutils' in sections:
                index_servers = config.get('distutils', 'index-servers')
                _servers = [server.strip() for server in
                            index_servers.split('\n')
                            if server.strip() != '']
                if _servers == []:
                    # nothing set, let's try to get the default pypi
                    if 'pypi' in sections:
                        _servers = ['pypi']
                    else:
                        # the file is not properly defined, returning
                        # an empty dict
                        return {}
                for server in _servers:
                    current = {'server': server}
                    current['username'] = config.get(server, 'username')
                    current['password'] = config.get(server, 'password')
                    
                    # optional params
                    if config.has_option(server,'repository'):
                        current['repository'] = config.get(server,'repository')
                    else:
                        current['repository'] = repository
                    
                    if (current['server'] == repository or 
                        current['repository'] == repository):
                        return current
            elif 'server-login' in sections:
                # old format
                server = 'server-login'
                if config.has_option(server, 'repository'):
                    repo = config.get(server, 'repository')
                else:
                    repo = repository
                return {'username':config.get(server,'username'),
                        'password':config.get(server,'password'),
                        'repository':repo,
                        'server':server}
        return {}
    
    usage = 'usage: %prog [options] arg [arg1 [arg2 ...]]'
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--repository',dest='repository',
                      default='http://localhost:8000/',
                      help='upload to REPOSITORY', metavar='REPOSITORY')
    parser.add_option('-c', '--config-file',dest='rcfile',
                      default=os.path.join(os.path.expanduser('~'),'.pypirc'),
                      help='full path for pypi config file')
    
    
    (options, args) = parser.parse_args()
    if not args:
        print '''No files to upload'''
        parser.print_help()
        parser.exit(1)

    # check we are dealing with a path to a dir
    # so we can recursively upload the files
    if not isdir(args[0]):
        print '''Not directory, exiting'''
        parser.print_help()
        parser.exit(1)
        
        
    config = read_rc_file(options.rcfile,options.repository)
    if config:
        repository = config['repository']
        username = config['username']
        password = config['password']
    else:
        print '''Could not find username and password details.
Check your pypi config file has these details and you are selecting the matching repository
'''
        parser.print_help()
        parser.exit(2)
    
    uploader = DumbUploader(repository,
                            username,
                            password)

    chdir(args[0])

    for filename in listdir(getcwd()):
        print filename
        if not filename.endswith('version_cache'):
            unpack(filename)
        #if os.path.exists(filename):
        #    if uploader.setDistFile(filename):
        #        uploader.register()
        #        uploader.bdist_dumb()
