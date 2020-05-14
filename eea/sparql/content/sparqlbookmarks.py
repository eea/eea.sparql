"""Definition of the SparqlBookmarks content type
"""

import logging

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager, SpecialUsers
from AccessControl.SecurityManagement import (newSecurityManager,
                                              setSecurityManager)
from eea.sparql.content.sparqlquery import generateUniqueId, SparqlQuery
from eea.sparql.interfaces import ISparqlBookmarksFolder
from plone import namedfile
from plone.dexterity.content import Container, DexterityContent
from plone.folder.ordered import CMFOrderedBTreeFolderBase
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import implementer

logger = logging.getLogger("eea.sparql")


@implementer(ISparqlBookmarksFolder)
class SparqlBookmarksFolder(Container, SparqlQuery):
    """Sparql Bookmarks Folder"""

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

    def checkQuery(self, title, endpoint, query):
        """Check if a query already exists
           0 - missing
           1 - exists
           2 - exists but changed"""
        found = False
        changed = True
        for sparql in self.values():
            if sparql.title == title:
                found = True

                if sparql.query_with_comments == query:
                    changed = False
                break

        if not found:
            return 0

        if not changed:
            return 1

        return 2

    def addOrUpdateQuery(self, title, endpoint, query):
        """Update an already existing query
           Create new version"""
        oldSecurityManager = getSecurityManager()
        newSecurityManager(None, SpecialUsers.system)
        ob = None

        changed = True

        for sparql in self.values():
            if sparql.title == title:
                ob = sparql

                if sparql.query_with_comments == query:
                    changed = False
                break

        if not ob:
            _id = generateUniqueId("SparqlQuery")
            try:
                _id = self.invokeFactory(type_name="SparqlQuery", id=_id, sparql_query=query)
            except:
                import pdb; pdb.set_trace()
                _id = self.invokeFactory(type_name="SparqlQuery", id=_id, sparql_query=query)
            ob = self[_id]

            setattr(ob, 'endpoint_url', endpoint)
            setattr(ob, 'sparql_query', query)
            # edit no longer accepting other params, useful for reindex
            ob.edit(
                title=title,
            )

            # generate new id
            normalizer = getUtility(IIDNormalizer)
            new_id = normalizer.normalize(title)

            ob.aq_parent.manage_renameObject(_id, new_id)
            ob.invalidateWorkingResult() # TODO: Use rabbitmq
        else:
            if changed:
                setattr(ob, 'sparql_query', query)
                if getattr(ob, 'reindexObject', None) is not None:
                    ob.reindexObject()
                ob.invalidateWorkingResult() # TODO: Use rabbitmq
        setSecurityManager(oldSecurityManager)

        return ob

    def findQuery(self, title):
        """Find the Query in the bookmarks folder
        """
        ob = None

        for sparql in self.values():
            if sparql.title == title:
                ob = sparql
                break
        return ob

    def syncQueries(self):
        """sync all queries from bookmarks"""
        queries = self.execute().get('result', {}).get('rows', {})
        for query in queries:
            query_name = query[0].value
            query_sparql = query[2].value
            self.addOrUpdateQuery(query_name,
                                  self.endpoint_url,
                                  query_sparql)
