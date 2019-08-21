'''Function plugins
=====================

Defines a plugin architecture so that new functions can be defined at runtime
and made available to the :attr:`ceed.function.FunctionFactoryBase`
used in the GUI and for later analysis.

When :mod:`ceed.function` is imported, it automatically calls
:func:`import_plugins` which imports all the ``.py`` files that don't start
with an underscore in ``ceed/function/plugin``.

Files in ``ceed/function/plugin`` that want to define new function classes
should define a function in the file called ``get_ceed_functions`` that returns
a list of functions that will be automatically registered with the function
factory :attr:`ceed.function.FunctionFactoryBase` using
:meth:`~ceed.function.FunctionFactoryBase.register`. See this
``ceed/function/plugin/__init__.py`` file for an example.
'''

import importlib
from os import listdir
from os.path import dirname
from math import exp, cos, pi

from kivy.properties import NumericProperty

from ceed.function import CeedFunc, FuncDoneException

__all__ = (
    'get_plugin_functions', 'ConstFunc', 'LinearFunc', 'ExponentialFunc',
    'CosFunc', 'get_ceed_functions')


def get_plugin_functions():
    '''Imports all the ``.py`` files that don't start with an underscore in
    ``ceed/function/plugin``. This is called by
    :func:`~ceed.function.register_all_functions`.
    '''
    funcs = list(get_ceed_functions())  # get functions from this file
    for name in listdir(dirname(__file__)):
        if name.startswith('_') or not name.endswith('.py'):
            continue
        name = name[:-3]
        m = importlib.import_module('ceed.function.plugin.{}'.format(name))
        funcs.extend(m.get_ceed_functions())
    return funcs


class ConstFunc(CeedFunc):
    '''Defines a function which returns a constant value.

    The function is defined as ``y(t) = a``.
    '''

    a = NumericProperty(0.)

    def __init__(self, name='Const', description='y(t) = a', **kwargs):
        super(ConstFunc, self).__init__(
            name=name, description=description, **kwargs)

    def __call__(self, t):
        super().__call__(t)
        return self.a

    def get_gui_props(self):
        d = super(ConstFunc, self).get_gui_props()
        d['a'] = None
        return d

    def get_state(self, *largs, **kwargs):
        d = super(ConstFunc, self).get_state(*largs, **kwargs)
        d['a'] = self.a
        return d

    def get_noise_supported_parameters(self):
        val = super(ConstFunc, self).get_noise_supported_parameters()
        val.add('a')
        return val


class LinearFunc(CeedFunc):
    '''Defines a linearly increasing function.

    The function is defined as ``y(t_in) = mt + b``, where
    ``t = (t_in - t_start + t_offset)``.
    '''

    m = NumericProperty(1.)

    b = NumericProperty(0.)

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Linear')
        kwargs.setdefault('description', 'y(t) = m(t + t_offset) + b')
        super(LinearFunc, self).__init__(**kwargs)

    def __call__(self, t):
        super().__call__(t)
        t = t - self.t_start + self.t_offset
        return self.m * t + self.b

    def get_gui_props(self):
        d = super(LinearFunc, self).get_gui_props()
        d['m'] = None
        d['b'] = None
        return d

    def get_state(self, *largs, **kwargs):
        d = super(LinearFunc, self).get_state(*largs, **kwargs)
        d['m'] = self.m
        d['b'] = self.b
        return d

    def get_noise_supported_parameters(self):
        val = super(LinearFunc, self).get_noise_supported_parameters()
        val.add('m')
        val.add('b')
        return val


class ExponentialFunc(CeedFunc):
    '''Defines a double exponential function.

    The function is defined as ``y(t_in) = Ae^-t/tau1 + Be^-t/tau2``, where
    ``t = (t_in - t_start + t_offset)``.
    '''

    A = NumericProperty(1.)

    B = NumericProperty(0.)

    tau1 = NumericProperty(1.)

    tau2 = NumericProperty(1.)

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Exp')
        kwargs.setdefault(
            'description',
            'y(t) = Ae^-(t + t_offset)/tau1 + Be^-(t + t_offset)/tau2')
        super(ExponentialFunc, self).__init__(**kwargs)

    def __call__(self, t):
        super().__call__(t)
        t = t - self.t_start + self.t_offset
        return self.A * exp(-t / self.tau1) + self.B * exp(-t / self.tau2)

    def get_gui_props(self):
        d = super(ExponentialFunc, self).get_gui_props()
        d['A'] = None
        d['B'] = None
        d['tau1'] = None
        d['tau2'] = None
        return d

    def get_state(self, *largs, **kwargs):
        d = super(ExponentialFunc, self).get_state(*largs, **kwargs)
        d['A'] = self.A
        d['B'] = self.B
        d['tau1'] = self.tau1
        d['tau2'] = self.tau2
        return d

    def get_noise_supported_parameters(self):
        val = super(ExponentialFunc, self).get_noise_supported_parameters()
        val.add('A')
        val.add('B')
        val.add('tau1')
        val.add('tau2')
        return val


class CosFunc(CeedFunc):
    '''Defines a cosine function.

    The function is defined as ``y(t_in) = Acos(2pi*f*t + th0*pi/180) + b``,
    where ``t = (t_in - t_start + t_offset)``.
    '''

    f = NumericProperty(1.)

    A = NumericProperty(1.)

    th0 = NumericProperty(0.)

    b = NumericProperty(0.)

    def __init__(self, **kwargs):
        kwargs.setdefault('name', 'Cos')
        kwargs.setdefault(
            'description', 'y(t) = Acos(2pi*f*t + th0*pi/180) + b')
        super(CosFunc, self).__init__(**kwargs)

    def __call__(self, t):
        super().__call__(t)
        t = t - self.t_start + self.t_offset
        return self.A * cos(
            2 * pi * self.f * t + self.th0 * pi / 180.) + self.b

    def get_gui_props(self):
        d = super(CosFunc, self).get_gui_props()
        d['f'] = None
        d['b'] = None
        d['A'] = None
        d['th0'] = None
        return d

    def get_state(self, *largs, **kwargs):
        d = super(CosFunc, self).get_state(*largs, **kwargs)
        d['f'] = self.f
        d['b'] = self.b
        d['A'] = self.A
        d['th0'] = self.th0
        return d

    def get_noise_supported_parameters(self):
        val = super(CosFunc, self).get_noise_supported_parameters()
        val.add('f')
        val.add('A')
        val.add('th0')
        val.add('b')
        return val


def get_ceed_functions():
    '''Returns all the functions defined in the file.
    '''
    return ConstFunc, LinearFunc, ExponentialFunc, CosFunc
