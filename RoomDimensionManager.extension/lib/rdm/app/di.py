# -*- coding: utf-8 -*-
"""Small, explicit dependency container compatible with IronPython 2.7."""
import inspect


class ServiceRegistration(object):
    def __init__(self, implementation, singleton, factory):
        self.implementation = implementation
        self.singleton = singleton
        self.factory = factory
        self.instance = None


class DependencyContainer(object):
    def __init__(self):
        self._services = {}

    def register_singleton(self, service_type, implementation):
        self._services[service_type] = ServiceRegistration(implementation, True, False)

    def register_transient(self, service_type, implementation):
        self._services[service_type] = ServiceRegistration(implementation, False, False)

    def register_factory(self, service_type, factory, is_singleton=False):
        self._services[service_type] = ServiceRegistration(factory, is_singleton, True)

    def resolve(self, service_type):
        if service_type not in self._services:
            raise KeyError("Service {0} is not registered.".format(service_type))
        registration = self._services[service_type]
        if registration.singleton and registration.instance is not None:
            return registration.instance
        if registration.factory:
            instance = registration.implementation(self)
        elif isinstance(registration.implementation, type):
            instance = self._build_instance(registration.implementation)
        else:
            instance = registration.implementation
        if registration.singleton:
            registration.instance = instance
        return instance

    def _build_instance(self, implementation):
        parameters = inspect.getargspec(implementation.__init__).args
        return implementation(*[self.resolve(parameter) for parameter in parameters if parameter != 'self'])
