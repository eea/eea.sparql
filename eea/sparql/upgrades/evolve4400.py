""" Migrate sparqls with the new arguments format (name:type query)
"""

import logging
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.app.async.interfaces import IAsyncService
from eea.sparql.content.sparql import async_updateLastWorkingResults
import DateTime

logger = logging.getLogger("eea.sparql.upgrades")

def restart_sparqls(context):
    """ Migrate sparqls with the new arguments format (name:type query)
    """

    async = getUtility(IAsyncService)
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql')

    restarted = 0
    for brain in brains:
        obj = brain.getObject()
        if obj.getRefresh_rate() != 'Once':
            obj.scheduled_at = DateTime.DateTime()
            async.queueJob(async_updateLastWorkingResults,
                            obj,
                            scheduled_at=obj.scheduled_at,
                            bookmarks_folder_added=False)
            restarted += 1

    message = 'Restarted %s Sparqls ...' %restarted
    logger.info(message)
    return message
