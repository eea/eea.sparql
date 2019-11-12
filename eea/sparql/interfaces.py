""" Sparql interfaces module
"""

from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


class ISparql(Interface):
    """ISparql"""


class ISparqlBookmarksFolder(ISparql):
    """ISparqlBookmarksFolder"""


class ISparqlBookmarksFolderAdded(IObjectEvent):
    """An event signalling that the sparql bookmarks folder was added
    """
