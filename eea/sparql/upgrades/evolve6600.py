""" 
"""

import logging
from Products.CMFCore.utils import getToolByName
from eea.sparql.converter.sparql2json import sparql2json
import transaction

logger = logging.getLogger("eea.sparql.upgrades")

def set_sparql_export_attribute(context):
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='Sparql', Language='all',
                                   show_inactive=True)

    log_total = len(brains)
    log_count = 0
    migrated = 0
    negative_export = 0
    for brain in brains:
        log_count += 1
        try:
            obj = brain.getObject()
        except Exception:
            logger.info('FAILED getObject %s:%s: %s', log_count, log_total,
                        brain.getPath())
            continue
        if getattr(obj, 'cached_result', None):
            logger.info('PATH %s:%s: %s', log_count, log_total, brain.getPath())

            setattr(obj, 'exportWorks', True)
            try:
                setattr(obj, 'exportWorks', True)
                setattr(obj, 'exportStatusMessage', '')
                sparql2json(obj.cached_result)
            except Exception, err:
                logger.info('Export status failed on: %s', brain.getPath())
                setattr(obj, 'exportWorks', False)
                setattr(obj, 'exportStatusMessage', err)
                negative_export += 1
                continue
            transaction.commit()
            migrated += 1
            if log_count % 100 == 0:
                logger.info('INFO: Transaction committed to zodb (%s/%s)',
                            log_count, log_total)
    message = 'Finished setting export status for %s Sparqls' % migrated
    logger.info(message)
    logger.info('%s items have export status set to False' % negative_export)
    return message