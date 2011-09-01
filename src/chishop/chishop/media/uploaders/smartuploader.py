#!/usr/bin/env python

"""Give this script the path to uploaded python libs and it will upload to
a egg server."""

from cStringIO import StringIO
from distutils.command.register import register
from distutils.command.upload import upload
from distutils.core import Distribution
import json
import re
from os import listdir, chdir, getcwd, unlink
from os.path import isdir
from shutil import rmtree
from pkginfo import BDist
import gzip, subprocess, sys, tarfile, zipfile

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
        print '%s registered... ' % (self.filename),
    
    def bdist_dumb(self):
        """Upload a binary distribution using the code version of:
        python setup.py sdist upload -r http://localhost:8000/ --show-response
        """
        command = 'bdist_dumb'
        
        pyversion = 'any'
        self.distribution.dist_files.append((command, pyversion, self.filename))
        distribution_upload = upload(self.distribution)
        distribution_upload.show_response = 1
        distribution_upload.username = self.username
        distribution_upload.password = self.password
        distribution_upload.repository = self.repository

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        distribution_upload.run()
        sys.stdout = old_stdout
        return mystdout.getvalue()

def unpack(filename):
    """Check what sort of package we have (tar.gz, zip or egg), unpack it and 
    get it uploaded."""

    if filename.endswith('.tar.gz') or filename.endswith('.zip'):
        return decompress(filename)

def decompress(filename):
    """Take either a zip or gz file and decompress it and untar it if needed."""

    UNPACK_DIR = '/tmp'

    def root_folder_name(compressed_file):
        if isinstance(compressed_file, zipfile.ZipFile):
            afile = compressed_file.namelist()[0]
        elif isinstance(compressed_file, tarfile.TarFile):
            afile = compressed_file.getnames()[0]

        if '/' in afile:
            afile = os.path.split(afile)[0]

        return afile

    if filename.endswith('.gz'):
        zipped_handle = gzip.open(filename, 'rb')
        file_contents = zipped_handle.read()
        
        # create a .tar file to decompress into
        tar_filename = os.path.join(
            UNPACK_DIR,
            filename.rsplit('.', 1)[0]
        )

        if tar_filename:
            output = open(tar_filename, 'wb')
            output.writelines(file_contents)
            output.close()
            zipped_handle.close()

            # test we have a tar file
            if tarfile.is_tarfile(tar_filename):
                tar_file = tarfile.TarFile(tar_filename)
                tar_file.extractall(path=UNPACK_DIR)
                folder_name = os.path.join(UNPACK_DIR,
                    root_folder_name(tar_file))
                tar_file.close()
                # Clean up the unnecessary tar file
                unlink(tar_filename)
                return folder_name

            else:
                print "Not a tar file!"
        else:
            print "Missing extension on filename"

    elif filename.endswith('.zip'):
        try:
            zipped_file = zipfile.ZipFile(filename)
            zipped_file.extractall(path=UNPACK_DIR)
            zipped_file.close()

            return os.path.join(UNPACK_DIR, root_folder_name(zipped_file))
        except:
            print "Unable to unzip file: %s" % (filename)

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

    def parse_response(stdout, stderr):
        if '\nServer response (200): OK' in stdout:
            print 'Upload successful'
            return True
        elif '\nUpload accepted.\n' in stdout:
            print 'Egg uploaded successfully'
            return True
        else:
            print 'UPLOAD FAILED:'
            if '[Errno 111] Connection refused' in stdout:
                print '\t', 'CONNECTION REFUSED'
            elif 'IOError: [Errno 2] No such file or directory: \'README.rst\'' in stderr:
                print '\t', 'Missing README.rst'
            else:
                spacer = re.compile('\n[-]{50,80}(.*)')
                server_response = spacer.search(stdout)
                if server_response:
                    print '\t', server_response.group(1).strip('-')
                else:
                    print '\n' + '-'*30
                    print stdout, stderr
                    print '\n' + '-'*30
            return False


    for filename in listdir(getcwd()):
        if not filename.endswith('version_cache'):
            if filename.endswith('.zip') or filename.endswith('.gz'):
                print "Uploading package: %s ..." % (filename),
                sys.stdout.flush()

                files_dir = unpack(filename)
                print files_dir

                if files_dir:
                    chdir(files_dir)
                    command = ['python', 'setup.py', 'sdist', 'upload', '-r',
                                                'chishop', '--show-response']
                    retcode = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    success = parse_response(*retcode.communicate())

                    # Change back to root to upload next file
                    chdir(args[0])
                    # Clean up
                    rmtree(files_dir)
                    # Record success
                    log_file_dir = '/tmp'
                    log_file = open(os.path.join(log_file_dir, 'smart.log'), 'a')
                    log_file.writelines(os.path.join(getcwd(), filename) + ' : ' + str(success) + ',\n')
                    log_file.close()
                else:
                    print 'UPLOAD FAILED: Could not unpack.'

            elif filename.endswith('egg'):
                print "Uploading package: %s ..." % (filename),

                if os.path.exists(filename):
                    if uploader.set_dist_file(filename):
                        uploader.register()
                        output = uploader.bdist_dumb()
                        parse_response(output, '')
                chdir(args[0])
            else:
                continue
