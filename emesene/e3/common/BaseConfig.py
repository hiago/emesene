'''defines base class for configuration'''
# -*- coding: utf-8 -*-

#    This file is part of emesene.
#
#    emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
log = logging.getLogger('e3.common.Config')

from Signal import WeakMethod

class Config(object):
    '''a class that contains all the configurations of the user,
    the config keys follow a convention, all the names start with
    the type they have, for example:
    b_foo is boolean
    i_bar is int
    f_baz is float
    l_lala is list
    d_argh is dict (key and value are strings)
    when you try to get an attribute, if it doesn't exist it will
    return None, if the parse fails the value will not be set,
    doing this allows you to get values and don't fill the code
    with try/excepts and validations, if the name doesn't contains
    one of those prefixes, it will return the value as string'''

    def __init__(self, **kwargs):
        '''constructor'''
        self.__dict__ = kwargs
        self._item_callbacks = None
        self._callbacks = None

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return None

    def __setattr__(self, item, value):
        object.__setattr__(self, item, value)
        self.notify_change(item, value)

    def get_or_set(self, name, default):
        '''return the value of the name config value, if not set
        then set it to default and return that value'''
        if name not in self.__dict__:
            self.__dict__[name] = default

        return self.__dict__[name]

    def notify_change(self, item, value):
        '''notify the callbacks that item has changed its value'''
        if self._callbacks is None:
            self._callbacks = []

        if self._item_callbacks is None:
            self._item_callbacks = {}

        for callback in self._callbacks:
            callback(item, value)

        for callback in self._item_callbacks.get(item, ()):
            callback(value)

    def subscribe(self, callback, item=None):
        '''add callback to the list of callbacks to be notified
        on an attribute change, if item is None then notify on
        all item changes, it item is a string, then notify on
        the change of that item'''
        callback = WeakMethod(callback)

        if self._callbacks is None:
            self._callbacks = []

        if self._item_callbacks is None:
            self._item_callbacks = {}

        if item is None:
            if callback not in self._callbacks:
                self._callbacks.append(callback)
        else:
            if item not in self._item_callbacks:
                self._item_callbacks[item] = []

            if callback not in self._item_callbacks[item]:
                self._item_callbacks[item].append(callback)

    def unsubscribe(self, callback, item=None):
        '''remove the callback from the callback list, if item is None
        try to remove the callback from the global callback list, if it's
        a string try to remove from the callback list of that item'''
        callbacks = []

        if item is None:
            callbacks = self._callbacks
        elif item in self._item_callbacks:
            callbacks = self._item_callbacks[item]


        to_remove = None
        for weakmethod in callbacks:
            if callback == weakmethod.f:
                to_remove = weakmethod

        if to_remove is not None:
            self._callbacks.remove(to_remove)

    def load(self, path, clear=False):
        '''load the config file from path, clear old values if
        clear is set to True'''
        raise NotImplementedError()

    def save(self, path):
        '''save to a config file'''
        raise NotImplementedError()

