""" Control panel
"""
from Products.Five import BrowserView
from zope.component import getUtility
from plone.app.async.interfaces import IAsyncService
from zc.async.interfaces import COMPLETED
from Products.CMFCore.utils import getToolByName
import DateTime
from eea.sparql.content.sparql import async_updateLastWorkingResults
import logging

class ScheduleStatus(BrowserView):
    """ Async Schedule Status of Sparql Queries
    """

    def __call__(self):
        self.async_service = getUtility(IAsyncService)
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.brains = self.catalog.searchResults(portal_type='Sparql')

        ob_path = self.request.get('sparql_ob_path', '')
        if ob_path:
            self.restartSparql(ob_path)

        self.updSparqlDetails()
        self.updQueueDetails()

        return super(ScheduleStatus, self).__call__()

    def updSparqlDetails(self):
        """Retrieves and stores details about sparql queries
        which have a repeatable refresh rate
        """

        self.sparql_details = {}

        ob_path = None
        for brain in self.brains:
            ob = brain.getObject()
            if ob.refresh_rate != 'Once':
                ob_path = brain.getPath()
                self.sparql_details[ob_path] = {
                    'ob_title':brain.Title,
                    'ob_url':brain.getURL(),
                    'ob_rrate':ob.refresh_rate,
                    'ob_scheduled_at':ob.scheduled_at
                    }

    def updQueueDetails(self):
        """Retrieves and stores details about sparql queued jobs"""

        self.queue_details = {}

        async_queue = self.async_service.getQueues()['']

        ob_path = None
        for job in async_queue:
            if job.status != COMPLETED:
                ob_path = '/'.join(job.args[0])
                self.queue_details[ob_path] = {
                    'job_status':job.status,
                    'job_scheduled_at':job.begin_after
                    }

    def getSparqlStatus(self):
        """Returns the view's results"""

        sparqls = set(self.sparql_details.keys())
        jobs = set(self.queue_details.keys())

        sparql_jobs = sparqls.intersection(jobs)

        results = []
        tmp_status = {}

        local_zone = DateTime.DateTime().asdatetime().tzinfo

        for ob_path in sparqls:
            tmp_status = {
                'path': ob_path,
                'title': self.sparql_details[ob_path]['ob_title'],
                'url': self.sparql_details[ob_path]['ob_url'],
                'rrate': self.sparql_details[ob_path]['ob_rrate'],
                'scheduled_for': None
                }
            if ob_path in sparql_jobs:
                tmp_status['scheduled_for'] = \
                    self.queue_details[ob_path]['job_scheduled_at'].\
                    astimezone(local_zone).strftime('%Y-%m-%d, %I:%M:%S %p')

            results.append(tmp_status)

        return results

    def restartSparql(self, ob_path):
        """Updates the results of a sparql query and schedules it in the
        async queue; the argument is the relative path of sparql object
        """

        brains = self.catalog.searchResults(portal_type='Sparql', path=ob_path)
        brain = brains[0]
        obj = brain.getObject()

        logger = logging.getLogger("eea.sparql")

        if obj and obj.getRefresh_rate() != 'Once':
            obj.scheduled_at = DateTime.DateTime()
            logger.info('[Restarting Sparql]: %s', brain.getURL())
            self.async_service.queueJob(async_updateLastWorkingResults,
                                    obj,
                                    scheduled_at=obj.scheduled_at,
                                    bookmarks_folder_added=False)
