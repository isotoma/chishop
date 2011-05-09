from distutils.command.register import register
from distutils.command.upload import upload
from distutils.core import Distribution
from pkginfo import BDist

FIELD_TRANSLATE = {'summary':'description',
                   'home_page':'url'}
DEF_AUTHOR = {'author':'unknown',
              'author_email':'unknown@unknown',}
DEF_FIELDS = {'version':'0.0.1',
              'name':'unknown',
              'url':'http://unknown/'}

class DumbUploader(object):
    
    def __init__(self, repository, username, password):
        self.repository = repository
        self.username = username
        self.password = password
        
        self.filename = None
        self.distribution = None
    
    def setDistFile(self,filename):
        self.filename = filename
        package = BDist(filename)
        
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
    
    def register(self):
        #python setup.py register -r chishop --show-response
        r = register(self.distribution)
        r.repository = self.repository
        r.run()
    
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
    
if __name__ == '__main__':
    repository = 'http://themoon.isotomadev.com:8000'
    username = 'admin'
    password = 'password'
    filename = '/home/gjm/projects/lilly/it_trunk/plone/cache/dist/wicked-1.1.6-py2.4.egg'
    
    uploader = DumbUploader(repository,username,password)
    uploader.setDistFile(filename)
    uploader.register()
    uploader.bdist_dumb()
