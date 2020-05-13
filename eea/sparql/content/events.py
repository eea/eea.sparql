""" Handle events
"""
import logging

from zope.lifecycleevent import IObjectCreatedEvent

from eea.sparql.content.sparqlquery import updateLastWorkingResults
from eea.sparql.interfaces import ISparqlBookmarksFolder
from Products.statusmessages.interfaces import IStatusMessage

logger = logging.getLogger("eea.sparql")


def bookmarksfolder_added(obj, evt):
    """On new bookmark folder automatically fetch all queries"""
    obj.syncQueries()


def sparql_modified(obj, evt):
    """ Flush cache when the object is modified and show a portal message
    """
    obj.invalidateSparqlCacheResults()

    anchor_url = '%s/@@view#sparql-stats' % obj.absolute_url()

    IStatusMessage(obj.REQUEST).addStatusMessage(
        'The data will be updated shortly, please check \
                    <a href="%s">the info</a> below.' % anchor_url,
        type='info')


def sparql_added_or_modified(obj, evt):
    """Update last working results when sparql is added or modified"""
    bookmarks_folder_added = False
    if ISparqlBookmarksFolder.providedBy(obj) and \
            IObjectCreatedEvent.providedBy(evt):
        bookmarks_folder_added = True

    updateLastWorkingResults(obj, bookmarks_folder_added)