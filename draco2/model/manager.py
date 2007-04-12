# vi: ts=8 sts=4 sw=4 et
#
# manager.py: the model manager
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: $

import logging
import threading

from draco2.model.model import Model


class ModelManager(object):
    """The model manager.

    The model manager acts as a global repository of models.
    """

    def __init__(self):
        """Constructor."""
        self.m_models = {}
        self.m_tsd = threading.local()

    @classmethod
    def _create(cls, api):
        """Factory method."""
        manager = cls()
        manager._load_models(api)
        if hasattr(api, 'changes'):
            manager._set_change_manager(api.changes)
        return manager

    def _load_models(self, api):
        """Load models."""
        from draco2.core.model import DracoModel
        model = DracoModel(api.database)
        self.add_model(model, True)
        clslist = api.loader.load_classes('__model__.py', Model,
                                          scope='__docroot__')
        for cls in clslist:
            model = cls(api.database)
            self.add_model(model, True)

    def _finalize(self):
        """Finalize the models (closes transactions)."""
        models = self.m_models.values()[:]
        try:
            models += self.m_tsd.models.values()
        except AttributeError:
            pass
        for model in models:
            model._finalize()
        self.m_tsd.__dict__.clear()

    def _set_change_manager(self, changes):
        """Use change manager `changes'."""
        ctx = changes.get_context('draco2.core.loader')
        ctx.add_callback(self._change_callback)
        ctx = changes.get_context('draco2.core.config')
        ctx.add_callback(self._change_callback)

    def _change_callback(self, api):
        """Reload the model."""
        logger = logging.getLogger('draco2.model.manager')
        logger.info('Reloading model (a change was detected).')
        self.m_models.clear()
        self._load_models(api)

    def model(self, name):
        """Return a model `name', or None if the model does not exist."""
        try:
            return self.m_tsd.models[name]
        except (AttributeError, KeyError):
            return self.m_models.get(name)

    def add_model(self, model, global_=False):
        """Add a model `model' to the model manager.

        If `global_' is True, the model will be active for all requests,
        otherwise it will be specific to the current request.
        """
        if not isinstance(model, Model):
            m = 'Expecting "Model" instance (got %s).'
            raise TypeError, m % model
        if global_:
            self.m_models[model.name] = model
        else:
            try:
                self.m_tsd.models[model.name] = model
            except AttributeError:
                self.m_tsd.models = { model.name : model }
