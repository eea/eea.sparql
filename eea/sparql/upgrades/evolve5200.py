""" Migrate cached_result attribute for sparql objects
"""

import logging
from Products.CMFCore.utils import getToolByName
import transaction

logger = logging.getLogger("eea.sparql.upgrades")


def migrate_sparql_cached_result(context):
    """ Migrate sparqls cached_result to a blob field
    """

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql', Language='all',
                                   show_inactive=True)

    log_total = len(brains)
    log_count = 0
    migrated = 0
    for brain in brains:
        log_count += 1
        logger.info('PATH %s::%s: %s', log_count, log_total, brain.getPath())
        try:
            obj = brain.getObject()
        except Exception:
            logger.info('FAILED getObject %s::%s: %s', log_count, log_total,
                        brain.getPath())
            continue

        if getattr(obj, 'cached_result', None):
            obj.setSparqlCacheResults(obj.cached_result)
            del obj.cached_result
            migrated += 1
            transaction.commit()
            if log_count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb (%s/%s)',
                            log_count, log_total)

    message = 'Migrated cached_result for %s Sparqls ...' % migrated
    logger.info(message)
    return message
