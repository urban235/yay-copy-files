# yay-copy-files
non blocking, copying from local host to multiple host as the following:

got file: [localhost] no file: [h1, h2, h3, h4, h5, h6, h7]
copying localhost-->h1 
got file: [localhost, h1]  no file: [h2, h3, h4, h5, h6, h7] 
copying localhost-->h2, h1-->h3
got file: [localhost, h1, h2, h3]  no file: [h4, h5, h6, h7] 
copying localhost-->h4, h1-->h5, h2-->h6, h3-->h7

using user name and password

# how to use:

` from copy_files import *`
`copy_manager('./doorp.py', ['ninjan40','ninjan43','ninjan42','ninjan41'])
`