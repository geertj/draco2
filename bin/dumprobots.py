#!/usr/bin/env python
#
# dumprobots.py: fetch robots list from www.robotstxt.org
#
# $Revision: 255 $

import time
import urllib

from draco2.util import http

url = 'http://www.robotstxt.org/wc/active/all.txt'
local = 'robots.local'
txtorg = 'robotstxt.org'
merged = 'robots.ini'
exclude = ('???', 'no', 'yes', 'none', 'not available')


print 'Downloading robot signatures from: %s' % url
robots = []
fin = urllib.urlopen(url)
for line in fin:
    if not line:
        break
    if not line.startswith('robot-useragent:'):
        continue
    agent = line[16:].strip().lower()
    if not agent or agent in exclude:
        continue
    agent, version, info = http.parse_user_agent(agent)
    if agent not in robots:
        robots.append(agent)
fin.close()
print 'Done (%d signatures)' % len(robots)

print 'Write: %s' % txtorg
robots.sort()
fout = file(txtorg, 'w')
for line in robots:
    fout.write(line + '\n')
fout.close()

print 'Read: %s' % local
fin = file(local)
for line in fin:
    if not line:
        break
    agent = line.strip().lower()
    if not agent or agent in exclude:
        continue
    if agent not in robots:
        robots.append(agent)
fin.close()

print 'Write: %s (%d signatures)' % (merged, len(robots))
robots.sort()
fout = file(merged, 'w')
fout.write('# Draco robots.ini files\n')
for line in robots:
    fout.write(line + '\n')
fout.close()

print """
PLEASE MAKE SURE TO VERIFY THE robots.ini FILE BEFORE USE.
THE DATA FROM THE NET CONTAINS MANY ERRORS AND WILL BLOCK
OUT IMPORTANT USER AGENTS."""
