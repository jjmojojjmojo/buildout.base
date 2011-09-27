"""
File to use with buildout.extensionscripts to dump a buildout.cfg-compatible
file with all values compounded into one file.
"""
import ConfigParser
from StringIO import StringIO
import os

def dump(buildout):
    config = ConfigParser.RawConfigParser()
    
    dumpfile = buildout['buildout'].get('dump-file', os.path.join(buildout['buildout']['directory'], 'buildout-dump.cfg'))
    no_empties = buildout['buildout'].get('dump-skip-empty', False)
    
    for part, settings in buildout.iteritems():
        config.add_section(part)
        for key, value in settings.iteritems():
            if no_empties and not value:
                continue
                
            config.set(part, key, value)
    
    if dumpfile:
        output = open(dumpfile, 'w+')
    else:
        output = StringIO()
    
    config.write(output)
    
    if buildout['buildout'].get('verbosity', 0) > 0: 
        output.seek(0)
        print output.read()
    
    output.close()
