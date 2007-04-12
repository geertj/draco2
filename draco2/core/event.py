# vi: ts=8 sts=4 sw=4 et
#
# event.py: event handling
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import os.path
import threading


class EventHandler(object):
    """Base class for all events.

    Events can be implemented by subclassing this class and providing
    one or more event methods.
    """


class EventManager(object):
    """Event manager.

    This object is used by Draco as a global repository of event handlers.
    """

    def __init__(self):
        """Constructor."""
        self.m_handlers = []  # Global handlers
        self.m_tsd = threading.local()  # Per request handlers

    @classmethod
    def _create(cls, api):
        """Factory method."""
        events = cls()
        cls = api.loader.load_class('__event__.py', EventHandler,
                                    scope='__docroot__')
        if cls:
            handler = cls()
            events.add_event_handler(handler, True)
        return events

    def _finalize(self):
        """Finalize the request."""
        self.m_tsd.__dict__.clear()

    def add_event_handler(self, handler, global_=False):
        """Add an event handler instance `handler'.

        If `global_' is True, the event handler will be in effect for all
        request. Otherwise, it will be effective for the current request
        only.
        """
        if not isinstance(handler, EventHandler):
            m = 'Expecting Event instance (got %s).'
            raise TypeError, m % type(handler)
        if global_:
            self.m_handlers.append(handler)
        else:
            try:
                self.m_tsd.handlers.append(handler)
            except AttributeError:
                self.m_tsd.handlers = [handler]

    def raise_event(self, event, *args):
        """Raise a single event `event'. """
        handlers = self.m_handlers[:]
        try:
            handlers += self.m_tsd.handlers
        except AttributeError:
            pass
        for handler in handlers:
            try:
                method = getattr(handler, event)
            except AttributeError:
                continue
            method(*args)
