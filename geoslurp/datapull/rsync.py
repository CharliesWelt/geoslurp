# This file is part of geoslurp.
# geoslurp is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.

# geoslurp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with Frommle; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Author Roelof Rietbroek (roelof@geod.uni-bonn.de), 2018

from geoslurp.datapull import CrawlerBase,  UriFile
import subprocess
import re

class Crawler(CrawlerBase):
    """Crawler wrapper around the rsync program calls the linux rsync utility"""
    def __init__(self,url,auth):
        super().__init__(url)
        self.auth=auth

    def parallelDownload(self,outdir,check=False):
        updated=[]
        if check:
            cmd=['rsync', '-avz', '--del','--update', self.auth.user +"@"+self.rooturl,outdir]
        else:
            cmd=['rsync', '-avz', '--del', self.auth.user +"@"+self.rooturl,outdir]

        for file in self.startrsync(cmd):
             updated.append(UriFile(file))
        return updated

    def startrsync(self,cmd):
        """Start rsync and returns the lsit of files as a generator"""
        #start command and catch output
        dryrun=subprocess.Popen(cmd,stdout=subprocess.PIPE, env={"RSYNC_PASSWORD":self.auth.passw})
        buf,stderr=dryrun.communicate()
        #skip rsync output, and directories
        skipregex=re.compile(b'(/$)|(receiving incremental)|(^$)|(sent.*bytes.*received)|(total size)')
        for ln in buf.splitlines():

            if skipregex.search(ln):
                continue
            yield ln.decode('utf-8')

    def  uris(self):
        pass

    def ls(self):
        """list remote content (using dry run)"""
        #write a tempoary passowrd file to /tmp
        cmd=['rsync', '-avz', '--del','--dry-run', self.auth.user +"@"+self.rooturl,'.']
        for file in self.startrsync(cmd):
            yield file

