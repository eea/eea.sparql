""" Sparql events
"""

from zope.interface import implementer
from zope.component.interfaces import ObjectEvent
from eea.sparql.interfaces import ISparqlBookmarksFolderAdded

@implementer(ISparqlBookmarksFolderAdded)
class SparqlBookmarksFolderAdded(ObjectEvent):
    """SparqlBookmarksFolder was added
    """
