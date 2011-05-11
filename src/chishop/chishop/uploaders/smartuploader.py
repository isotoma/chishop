#!/usr/bin/env python

"""Give this script the path to uploaded python libs and it will upload to
a egg server."""

from distutils.command.register import register
from distutils.command.upload import upload
from distutils.core import Distribution
from os import listdir, chdir, getcwd
from os.path import isdir
from pkginfo import BDist
import gzip, subprocess, tarfile, zipfile

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
    
    def set_dist_file(self, filename):
        """Setup our distribution using details from the binary"""
        self.filename = filename
        try:
            package = BDist(filename)
        except ValueError, e:
            print e
            return False
        
        metadata = dict([(k, getattr(package, k)) for k in package.iterkeys()
                         if getattr(package, k)])
        
        for (inkey, outkey) in FIELD_TRANSLATE.iteritems():
            if getattr(package, inkey, None):
                metadata[outkey] = metadata[inkey]
                del metadata[inkey]
        
        got_a = 'author' in metadata and 'author_email' in metadata
        got_m = 'maintainer' in metadata and 'maintainer_email' in metadata
        if not(got_a or got_m):
            for (k, v) in DEF_AUTHOR.iteritems():
                if k not in metadata:
                    metadata[k] = v
        
        for (k, v) in DEF_FIELDS.iteritems():
            if k not in metadata:
                metadata[k] = v
        
        self.distribution = Distribution(metadata)
        return True
    
    def register(self):
        """Register a distribution code version of:
        python setup.py register -r chishop --show-response
        """
        r = register(self.distribution)
        r.repository = self.repository
        r.run()
        print '%s registered' % (self.filename)
    
    def bdist_dumb(self):
        """Upload a binary distribution using the code version of:
        python setup.py sdist upload -r http://localhost:8000/ --show-response
        """
        command = 'bdist_dumb'
        
        pyversion = 'any'
        self.distribution.dist_files.append((command, pyversion, self.filename))
        distribution_upload = upload(self.distribution)
        distribution_upload.username = self.username
        distribution_upload.password = self.password
        distribution_upload.repository = self.repository
        distribution_upload.run()
        print '%s uploaded' % (self.filename)

def unpack(filename):
    """Check what sort of package we have (tar.gz, zip or egg), unpack it and 
    get it uploaded."""

    if filename.endswith('.tar.gz') or filename.endswith('.zip'):
        if decompress(filename):
            return True

def decompress(filename):
    """Take either a zip or gz file and decompress it and untar it if needed."""    
    
    failed = False
    print filename
    if filename.endswith('.gz'):
        print getcwd()
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
                print "Not a tar file!"
                failed = True
        else:
            print "Missing extension on filename"
            failed = True

    elif filename.endswith('.zip'):
        try:
            zipped_file = zipfile.ZipFile(filename)
            zipped_file.extractall()
            zipped_file.close()
        except:
            print "Unable to unzip file: %s" % (filename)
            failed = True

    return failed

if __name__ == '__main__':
    from optparse import OptionParser
    from ConfigParser import ConfigParser
    import os.path
    
    def read_rc_file(f, repository):
        '''stolen from distutils.config'''
        if os.path.exists(f):
            config_parser = ConfigParser()
            config_parser.read(f)
            sections = config_parser.sections()
            if 'distutils' in sections:
                index_servers = config_parser.get('distutils', 'index-servers')
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
                    current['username'] = config_parser.get(server, 'username')
                    current['password'] = config_parser.get(server, 'password')
                    
                    # optional params
                    if config_parser.has_option(server,'repository'):
                        current['repository'] = config_parser.get(server,'repository')
                    else:
                        current['repository'] = repository
                    
                    if (current['server'] == repository or 
                        current['repository'] == repository):
                        return current
            elif 'server-login' in sections:
                # old format
                server = 'server-login'
                if config_parser.has_option(server, 'repository'):
                    repo = config_parser.get(server, 'repository')
                else:
                    repo = repository
                return {'username':config.get(server,'username'),
                        'password':config.get(server,'password'),
                        'repository':repo,
                        'server':server}
        return {}
    
    usage = 'usage: %prog [options] arg [arg1 [arg2 ...]]'
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--repository', dest='repository',
                      default='http://localhost:8000/',
                      help='upload to REPOSITORY', metavar='REPOSITORY')
    parser.add_option('-c', '--config-file', dest='rcfile',
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
        
        
    config = read_rc_file(options.rcfile, options.repository)
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
            if not filename.endswith('egg'):
                unpack(filename)
                if filename.endswith('.zip'):
                    files_dir = filename.rsplit('.', 1)[0]
                elif filename.endswith('.gz'):
                    files_dir = filename.rsplit('.', 2)[0]
                    
                chdir(files_dir)
                retcode = subprocess.Popen(["python", "setup.py", "sdist", "upload", "-r", "local", "--show-response"], 
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = retcode.communicate()[0]
                
                if not output.split('\n')[-3].count('200'):
                    print "failed to upload: %s" % (output.split('\n')[-2].replace('-', ''))
                
            elif filename.endswith('egg'):
                if os.path.exists(filename):
                    if uploader.set_dist_file(filename):
                        uploader.register()
                        uploader.bdist_dumb()
        chdir(args[0])
