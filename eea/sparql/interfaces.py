""" Sparql interfaces module
"""

from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface

from eea.sparql import sparqlMessageFactory as _
from plone.supermodel import model


class ISparql(Interface):
    """
    """


class ISparqlQuery(model.Schema, ISparql):
    """ISparql"""

    sparql_query = schema.Text(
        title=_(u'Sparql query'),
        required=True
    )

    endpoint = schema.URI(
        title=_(u'Sparql endpoint URL'),
        required=True,
        default="https://semantic.eea.europa.eu/sparql"
    )


class ISparqlBookmarksFolder(ISparql):
    """ISparqlBookmarksFolder"""


class ISparqlBookmarksFolderAdded(IObjectEvent):
    """An event signalling that the sparql bookmarks folder was added
    """
