# vi: ts=8 sts=4 sw=4 et
#
# robot.py: web robot detection
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os
import bisect
import logging


class RobotSignatures(object):
    """A repository of robot signatures.

    The repository is used for detecting web robots by matching their
    'User-Agent' HTTP header.
    """

    def __init__(self):
        """Constructor."""
        self.m_robots = []
        self.m_files = []
        self.m_change_context = None

    @classmethod
    def _create(cls, api):
        """Factory method."""
        robots = cls()
        robots._set_change_manager(api.changes)
        section = api.config.ns('draco2')
        datadir = section['datadirectory']
        path = os.path.join(datadir, 'robots.ini')
        robots.add_file(path)
        docroot = section['documentroot']
        path = os.path.join(docroot, 'robots.ini')
        robots.add_file(path)
        return robots

    def _set_change_manager(self, changes):
        """Use change manager `changes'."""
        self.m_change_context = changes.get_context('draco2.draco.robot')
        self.m_change_context.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Change manager callback (when files in the ctx change)."""
        self.m_robots = []
        for fname in self.m_files:
            self._parse_file(fname)
        logger = logging.getLogger('draco2.draco.robot')
        logger.debug('Reloaded robot signatures (change detected).')

    def add_file(self, fname):
        """Load robot signatures from file `fname'."""
        self.m_files.append(fname)
        self._parse_file(fname)
        if self.m_change_context:
            self.m_change_context.add_file(fname)

    def _parse_file(self, fname):
        """Parse a robot signatures file."""
        try:
            fin = file(fname)
        except IOError:
            return
        for line in fin:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            self.m_robots.append(line.lower())
        fin.close()
        self.m_robots.sort()

    def match(self, agent):
        """Match user agent string `agent' against the signatures.

        The match operation done is a prefix match, i.e. we have a match
        if `agent' matches a prefix of a registered signature.
        """
        agent = agent.lower()
        i = bisect.bisect_right(self.m_robots, agent)
        return i > 0 and agent.startswith(self.m_robots[i-1])
