#!/usr/bin/python

# Copyright (c) 2005, Toby White <tow21@cam.ac.uk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions 
# are met:
#
#     * Redistributions of source code must retain the above copyright 
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above 
# copyright notice, this list of conditions and the following disclaimer 
# in the documentation and/or other materials provided with the 
# distribution.
#     * The name of Toby White may not be used to endorse or promote 
# products derived from this software without specific prior written 
# permission.
#     * Any individuals or entities associated with the San Diego 
# Supercomputing Centre may not use, modify, or redistribute this code 
# in any form without the explicit permission of the copyright holder.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS 
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND 
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR 
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 



import cgi
import cgitb; cgitb.enable()
import os
import stat
import sys
import time
import tempfile
import urllib

# Nothing below this line should be altered.
############################################

# CGI environment variables of interest.
thisServer = os.environ['SERVER_NAME']
thisPage = os.environ['SCRIPT_NAME']
thisPage = 'http://CMLComp.org/validator/'
if os.environ.has_key('HTTP_ACCEPT'):
    httpAccept = os.environ['HTTP_ACCEPT']
else:
    httpAccept = 'text/html'

# Check if user is using IE or other dumb browser
if httpAccept.find('application/xhtml+xml') > -1:
    contentType = "application/xhtml+xml"
else:
    contentType = 'text/html'

# Templates for output file.
#########################################

header = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>CMLComp Validator</title>
    <link rel="shortcut icon" href="/CMLComp.ico" type="image/vnd.microsoft.icon"/>
    <link rel="stylesheet" type="text/css" href="/style.css"/>
  </head>
  <body>
    <p><object type="image/png" data="/CMLComp.logo.png"><h1>CMLComp</h1></object></p>
    <h2><span class="smallcaps">CMLComp</span> Validator</h2>
"""

htmlForm = """
  <p>Choose a CML file, pick a schema below, and press <strong>Validate</strong>.</p>
  <div id="inputForms">
    <form method="post" action="%(thisPage)s" enctype="multipart/form-data" onsubmit="submitForm(this.id)" id="putForm">
        <p><span class="smallcaps">CMLComp</span> file: <input name="xmlUp" value="" type="file"/></p>
        <p>
        <table>
          <tr><th/><th>Schema type</th></tr>
          <tr><td><input type="radio" name="schema" value="http://uszla.me.uk/gitweb/CMLComp.git/master:/CMLComp/CMLComp-micro-full.rng" checked="yes"/></td><td>Microstructure</td></tr>
          <tr><td><input type="radio" name="schema" value="http://uszla.me.uk/gitweb/CMLComp.git/master:/CMLComp/CMLComp-doc-full.rng"/></td><td>Document structure and microstructure</td></tr>
        </table>
        </p>
        <p><em>(This validation will occur against the latest development version of the schema. If you find your CML unexpectedly rejected, please <a href="http://cmlcomp.org/t/newticket">file a bug</a> or send an example to the <a href="http://www.uszla.me.uk/cgi-bin/mailman/listinfo/cmlcomp/">mailing list</a>.<br/>
        Please note, however, the <a href="http://cmlcomp.org/t/wiki/CommonErrors">list of common errors</a> on the wiki.)</em></p>
      <p><input value="Validate" type="submit"/></p>
    </form>
  </div>
"""

footer = """
  <div>
    <p>This validator service relies on Henri Sivonen's excellent <a href="http://validator.nu">validator.nu</a>.</p>
    <p>You can also validate your files from the command line. See <a href="http://cmlcomp.org/t/wiki/ConformanceCheckers">the wiki</a> for details.</p>
  </div>
  </body>
</html>
"""

# Exception classes.
#########################################

class Page:
    def __init__(self, contentType='text/plain', status=200, statusmsg='OK'):
	self.headers = {}
	self.headers['Content-Type'] = contentType
	self.headers['Status'] = str(status)+' '+statusmsg
	self.contents = []

    def appendHeaders(self, headers):
	for key in headers:
	    self.headers[key] = headers[key]

    def append(self, line):
	self.contents.append(line)

    def write(self, output=sys.stdout):
	for key in self.headers:
	    output.write(key+': '+self.headers[key]+'\n')
	output.write('\n')
	for line in self.contents:
	    output.write(line+'\n')

def xmlEncode(string):
    tempstring = string.replace("&", '&amp;')
    tempstring = tempstring.replace('<', '&lt;')
    tempstring = tempstring.replace('"', '&quot;')
    tempstring = tempstring.replace("'", '&apos;')
    return tempstring

def errorPage(errorCode, errorString, explanation):
    page = Page(contentType, errorCode, errorString)
    page.append(header % {'title':'ERROR'})
    page.append("<div class='error'><p>Error:</p>")
    page.append("<p>Status " + str(errorCode) + ' ' + xmlEncode(errorString) + "</p>")
    page.append("<p>"+xmlEncode(explanation)+"</p></div>")
    page.append(footer)
    return page

def generate_form():
    page = Page(contentType)
    page.append(header)
    page.append(htmlForm % {'thisPage':thisPage})
    page.append(footer)
    return page

def main():
    global contentType
    form = cgi.FieldStorage(keep_blank_values=True)
    if os.environ["REQUEST_METHOD"] == "GET":
        page = generate_form()
        return page
    elif os.environ["REQUEST_METHOD"] == "POST":
        try:
            postFile = form['xmlUp']
        except KeyError:
            page = generate_form()
            return page
        try:
            schema = form['schema'].value
        except KeyError:
            page = generate_form()
            return page
    global tmpDir, webDir
    tmpDir = tempfile.mkdtemp()
    webDir = os.path.join('/var/www/cmlcomp/validator/public', tmpDir[1:])
    os.makedirs(webDir)
    os.chmod(tmpDir, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    os.chmod(webDir, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    localFileName = os.path.join(tmpDir, 'postFile.xml')
    webFileName = os.path.join(webDir, 'postFile.xml')
    os.symlink(localFileName, webFileName)
    fUp = open(localFileName, 'wb')
# FIXME Ought to put a check in here to prevent DOS attacks
    while True:
        chunk = postFile.file.read(100000)
        if not chunk: break
        fUp.write (chunk)
    fUp.close()
    page = Page(contentType, status=303)
    headers = {}
    headers['Location'] = 'http://validator.nu/?schema='+urllib.quote(schema)+'&doc='+urllib.quote('http://cmlcomp.org/validator/public'+tmpDir+'/postFile.xml')
    page.appendHeaders(headers)
    return page
    
# Main program.
#########################################

tmpDir = ""
webDir = ""

#try:
page = main()
#except OSError, inst:
#    page = errorPage(400, 'Mysterious failure', 'Dont know what failed')
    
if page: page.write()
# Sleep for 120 seconds - hopefully that's long enough for validator.nu
# to do its stuff
os.system("nohup /var/www/cmlcomp/validator/tmpreap "+tmpDir+" "+webDir+"< /dev/null > /dev/null 2>&1")

