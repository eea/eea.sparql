"""Definition of the SparqlBookmarks content type
"""

import logging

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager, SpecialUsers
from AccessControl.SecurityManagement import (newSecurityManager,
                                              setSecurityManager)
# from eea.versions import versions # TODO: Port eea.versions
# from eea.versions.interfaces import IGetVersions
from eea.sparql.content.sparqlquery import generateUniqueId, SparqlQuery
from eea.sparql.interfaces import ISparqlBookmarksFolder
# from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import implementer


logger = logging.getLogger("eea.sparql")


@implementer(ISparqlBookmarksFolder)
class SparqlBookmarksFolder(Container, SparqlQuery):
    """Sparql Bookmarks Folder"""

    security = ClassSecurityInfo()

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
                break
                # import pdb; pdb.set_trace()
                latest_sparql = IGetVersions(sparql).latest_version()
                found = True

                if latest_sparql.query_with_comments == query:
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
                break
                # import pdb; pdb.set_trace() # IGetVersions not available yet
                x1 = IGetVersions(sparql)
                latest_sparql = x1.latest_version()
                ob = latest_sparql

                if latest_sparql.query_with_comments == query:
                    changed = False

                break

        if not ob:
            _id = generateUniqueId("SparqlQuery")
            _id = self.invokeFactory(type_name="SparqlQuery", id=_id)
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
            # ob.invalidateWorkingResult() # TODO: Reimplement when async is available
        else:
            if changed:
                pass # TODO: versions not ported yet
                ob = versions.create_version(ob)
                setattr(ob, 'sparql_query', query)
                if getattr(ob, 'reindexObject', None) is not None:
                    ob.reindexObject()
                # ob.invalidateWorkingResult() # TODO: Reimplement when async is available

        setSecurityManager(oldSecurityManager)

        return ob

    def findQuery(self, title):
        """Find the Query in the bookmarks folder
        """
        ob = None

        for sparql in self.values():
            if sparql.title == title:
                ob = sparql
                break # IGetVersions not available yet
                # import pdb; pdb.set_trace()
                latest_sparql = IGetVersions(sparql).latest_version()
                ob = latest_sparql

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
