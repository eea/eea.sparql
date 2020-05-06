""" Main product initializer
"""
from Products.CMFPlone import interfaces as Plone
from zope.interface import implementer
from zope.i18nmessageid import MessageFactory

sparqlMessageFactory = MessageFactory('eea.sparql')


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
