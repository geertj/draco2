# vi: ts=8 sts=4 sw=4 et
#
# request.py: request object for Draco handlers
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import os.path

from draco2.core.request import Request
from draco2.draco import uri as dracouri
from draco2.draco.robot import RobotSignatures
from draco2.util import http
from draco2.util.singleton import singleton


class DracoRequest(Request):
    """The Draco request object."""

    def __init__(self, iface):
        """Constructor."""
        super(DracoRequest, self).__init__(iface)
        self._parse_draco_uri()
        self._init_agent_info()
        self._set_robots(None)

    @classmethod
    def _create(cls, api):
        """Factory method."""
        request = cls(api.iface)
        robots = singleton(RobotSignatures, api,
                           factory=RobotSignatures._create)
        request._set_robots(robots)
        return request

    def _set_robots(self, robots):
        """Set the robot signature database."""
        if robots and not isinstance(robots, RobotSignatures):
            raise TypeError, 'Expecting a RobotSignatures instance.'
        self.m_robots = robots
        self._init_robot()

    def _parse_draco_uri(self):
        """Parse the request URI."""
        (protocol, host, directory, filename, locale, session,
         pathinfo, args) = dracouri.parse_draco_uri(self.uri(), self.docroot())
        self.m_locale = locale
        self.m_session = session
        self.m_pathinfo = pathinfo.split('/')

    def locale(self):
        """Return the request locale."""
        return self.m_locale

    def session(self):
        """Return the session presented in the request."""
        return self.m_session

    def _init_agent_info(self):
        """Parse the `User-Agent' header."""
        self.m_agentinfo = None
        agent = self.header('User-Agent')
        if not agent:
            return
        agentinfo = http.parse_user_agent(agent)
        self.m_agentinfo = agentinfo

    def agent_info(self):
        """Return parsed user agent info."""
        return self.m_agentinfo

    def _init_robot(self):
        """Match the `User-Agent' header against the robot database."""
        self.m_isrobot = False
        if not self.m_agentinfo or not self.m_robots:
            return
        signatures = [self.m_agentinfo[0]] + self.m_agentinfo[2]
        for sig in signatures:
            if self.m_robots.match(sig):
                self.m_isrobot = True
                break

    def isrobot(self):
        """Return nonzero if the a web robot is detected."""
        return self.m_isrobot
