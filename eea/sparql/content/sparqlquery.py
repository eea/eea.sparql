"""Definition of the Sparql content type
"""

import logging
from random import random

from zope.event import notify
from zope.interface import implementer
from zope.globalrequest import getRequest
from ZODB.POSException import POSKeyError

import DateTime
import pickle as cPickle
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from eea.sparql.cache import cacheSparqlKey, ramcache, cacheSparqlMethodKey
from eea.sparql.converter.sparql2json import sparql2json
from eea.sparql.events import SparqlBookmarksFolderAdded
from eea.sparql.interfaces import ISparqlQuery
from plone import namedfile
from plone.dexterity.content import Container, DexterityContent
from plone.folder.ordered import CMFOrderedBTreeFolderBase
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.ZSPARQLMethod.Method import (QueryTimeout, ZSPARQLMethod,
                                           interpolate_query, map_arg_values,
                                           parse_arg_spec,
                                           query_and_get_result,
                                           raw_query_and_get_result,
                                           run_with_timeout)


logger = logging.getLogger("eea.sparql")

RESULTS_TYPES = {
    'xml': "application/sparql-results+xml",
    'xmlschema': "application/x-ms-access-export+xml",
                 'json': "application/sparql-results+json"
}


@implementer(ISparqlQuery)
class SparqlQuery(Container, ZSPARQLMethod):
    """ Sparql query implementaiton in dexterity"""

    security = ClassSecurityInfo()
    # __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, id=None, **kwargs):
        """ Initialize cache fields """
        CMFOrderedBTreeFolderBase.__init__(self, id)
        DexterityContent.__init__(self, id, **kwargs)

        self.sparql_results_cached = namedfile.NamedBlobFile()
        self.sparql_results_cached_json = namedfile.NamedBlobFile()
        self.sparql_results_cached_xml = namedfile.NamedBlobFile()
        self.sparql_results_cached_xmlschema = namedfile.NamedBlobFile()
        self.sparql_results_are_cached = False

    @security.protected('View')
    def index_html(self, REQUEST=None, **kwargs):
        """ Public method, needs docstring
        """

        return self.__call__()

    @property
    def query(self):
        """query"""

        return "\n".join(x for x in self.sparql_query.splitlines()
                         if not x.strip().startswith("#"))

    @property
    def query_with_comments(self):
        """query"""

        return self.sparql_query

    @ramcache(cacheSparqlKey, dependencies=['eea.sparql'])
    @security.public
    def execute_query(self, args=None):
        """execute query"""
        arg_string = ' '.join([arg['name'] for arg in self.arg_spec or []])
        arg_spec = parse_arg_spec(arg_string)
        arg_values = map_arg_values(arg_spec, args)[1]

        return self.execute(**self.map_arguments(**arg_values))

    @security.public
    def getTimeout(self):
        """timeout"""
        return str(self.timeout)

    @security.public
    def setTimeout(self, value):
        """timeout"""
        try:
            self.timeout = int(value)
        except Exception:
            self.timeout = 10

    @ramcache(cacheSparqlMethodKey, dependencies=['eea.sparql'])
    def _getCachedSparqlResults(self):
        """
        :return: Cached Sparql results
        :rtype: object
        """
        empty_result = {"result": {"rows": "", "var_names": "",
                                    "has_result": ""}}
        try:
            data = self.sparql_results_cached.data
        # 69841 take into account missing blobs
        except POSKeyError:
            return empty_result
        # 69841 make sure the data returned can be pickled
        try:
            return cPickle.loads(data)
        except cPickle.UnpicklingError:
            return empty_result

    @security.public
    def getSparqlCacheResults(self):
        """
        :return: Sparql results
        :rtype: object
        """
        if getattr(self, 'sparql_results_are_cached', None):
            return self._getCachedSparqlResults()

        field = self.sparql_results_cached
        empty_result = {"result": {"rows": "", "var_names": "",
                                    "has_result": ""}}

        if field is None:
            return empty_result
        if field.getSize() == 0:
            return empty_result

        return cPickle.loads(field.data) if field and field.data else \
            empty_result

    @security.protected('View')
    def setSparqlCacheResults(self, result):
        """ Set Sparql Cache results
        """
        self.updateExportStatus(result)
        self.sparql_results_are_cached = True
        self.sparql_results_cached._setData(cPickle.dumps(result))

    @security.protected('View')
    def invalidateSparqlCacheResults(self):
        """ Invalidate sparql results
        """
        self.sparql_results_are_cached = False
        self.sparql_results_cached._setData(b"")

    @security.protected('View')
    def updateExportStatus(self, result):
        """ Update export status of HTML/CSV/TSV
        """
        setattr(self, 'exportWorks', True)
        try:
            setattr(self, 'exportWorks', True)
            setattr(self, 'exportStatusMessage', '')
            sparql2json(result)
        except Exception as err:
            logger.exception(err)
            setattr(self, 'exportWorks', False)
            setattr(self, 'exportStatusMessage', err)
        self._p_changed = True
        self.reindexObject()

    # TIBI: commented this method to use the default in Products.ZSPARQLMethod
    # @security.protected(view)
    # def execute(self, **arg_values):
    #     """ override execute, if possible return the last working results
    #     """
    #     cached_result = self.getSparqlCacheResults()
    #
    #     if not arg_values:
    #         return cached_result
    #
    #     self.updateLastWorkingResults(**arg_values)
    #
    #     return cached_result

    @security.protected(view,)
    def map_arguments(self, **arg_values):
        """ overides map_arguments to match the name:type - query data model
        """
        arg_string = ' '.join([arg['name'] for arg in (self.arg_spec or [])])
        arg_spec = parse_arg_spec(arg_string)

        if arg_values in [None, [], {}]:
            arg_values = {}
            for spec in self.arg_spec:
                key = spec['name'].split(':')[0]
                value = spec['query']
                arg_values.update({key: value})
        missing, arg_values = map_arg_values(arg_spec, arg_values)

        if missing:
            raise KeyError("Missing arguments: %r" % missing)
        else:
            return arg_values

    security.declareProtected(view, 'updateLastWorkingResults')
    def updateLastWorkingResults(self, **arg_values):
        """ update cached last working results of a query (json exhibit)
        """
        cached_result = self.getSparqlCacheResults()
        if arg_values in [{}, [], None]:
            arg_values = self.map_arguments()
        cooked_query = interpolate_query(self.query, arg_values)
        args = (self.endpoint_url, cooked_query)
        try:
            new_result = run_with_timeout(
                max(getattr(self, 'timeout', 10), 10),
                query_and_get_result,
                *args)
        except QueryTimeout:
            new_result = {'exception': "query has ran - an timeout has"
                                       " been received"}
        force_save = False

        if new_result.get("result", {}) != {}:
            if new_result != cached_result:
                if new_result.get("result", {}).get("rows", {}):
                    force_save = True
                else:
                    if not cached_result.get('result', {}).get('rows', {}):
                        force_save = True

        comment = "query has run - no result changes"
        if force_save:
            self.setSparqlCacheResults(new_result)
            self._updateOtherCachedFormats(self.endpoint_url, cooked_query)

            new_sparql_results = []
            rows = new_result.get('result', {}).get('rows', {})
            if rows:
                for row in rows:
                    for val in row:
                        if val is None:
                            new_sparql_results.append("" + " | ")
                        else:
                            new_sparql_results.append(val.value + " | ")
                new_sparql_results[-1] = new_sparql_results[-1][0:-3]
            new_sparql_results_str = "".join(new_sparql_results) + "\n"
            self.sparql_results = new_sparql_results_str
            comment = "query has run - result changed"

        request = getRequest()
        messages = IStatusMessage(request)
        messages.add(u"Query Saved. %s" % comment, type=u"warn")

        if new_result.get('exception', None):
            cached_result['exception'] = new_result['exception']
            self.setSparqlCacheResults(cached_result)

    def _updateOtherCachedFormats(self, endpoint, query):
        """ Run and store queries in sparql endpoints for xml, xmlschema, json
        """

        for _type, accept in RESULTS_TYPES.items():
            updateOtherCachedFormats(self, endpoint, query, _type, accept)

    security.declareProtected(view, 'invalidateWorkingResult')
    def invalidateWorkingResult(self):
        """ invalidate working results"""
        self.sparql_results = ""
        self.invalidateSparqlCacheResults()

        pr = getToolByName(self, 'portal_repository')
        comment = "Invalidated last working result"
        comment = comment.encode('utf')
        pr.save(obj=self, comment=comment)

        updateLastWorkingResults(self, False)


def generateUniqueId(type_name):
    """ generateUniqueIds for sparqls
    """
    now = DateTime.DateTime()
    time = '%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
    rand = str(random())[2:6]
    prefix = ''
    suffix = ''

    if type_name is not None:
        prefix = type_name.replace(' ', '_') + '.'
    prefix = prefix.lower()

    return prefix + time + rand + suffix


def updateLastWorkingResults(obj, bookmarks_folder_added=False):
    """ Update last working results
    """
    obj.updateLastWorkingResults()

    if bookmarks_folder_added:
        event = SparqlBookmarksFolderAdded(obj)
        notify(event)
        bookmarks_folder_added = False


def updateOtherCachedFormats(obj, endpoint, query, _type, accept):
    """ Updates json, xml, xmlschema exports, TODO: Port to rabbitmq
    """

    timeout = max(getattr(obj, 'timeout', 10), 10)
    try:
        new_result = run_with_timeout(
            timeout,
            raw_query_and_get_result, endpoint, query, accept=accept
        )
    except QueryTimeout:
        new_result = ""
        logger.warning(
            "Query received timeout: %s with %s\n %s \n %s",
            "/".join(obj.getPhysicalPath()), _type, endpoint, query
        )
        return

    fieldName = "sparql_results_cached_" + _type
    _attr = getattr(obj, fieldName)

    try:
        result = new_result['result'].read()
    except Exception:
        result = ""
        logger.warn(
            "Unable to read result from query: %s with %s\n %s \n %s",
            "/".join(obj.getPhysicalPath()), _type, endpoint, query
        )
    _attr._setData(cPickle.dumps(result))
