"""Definition of the SparqlBookmarks content type
"""

import logging

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager, SpecialUsers
from AccessControl.SecurityManagement import (newSecurityManager,
                                              setSecurityManager)
from eea.versions import versions
from eea.versions.interfaces import IGetVersions
from eea.sparql.content.sparqlquery import generateUniqueId, SparqlQuery
from eea.sparql.interfaces import ISparqlBookmarksFolder
# from Products.CMFCore.utils import getToolByName
from plone.dexterity.content import Container
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
            import pdb; pdb.set_trace()
            if sparql.title == title.encode('utf8'):
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
                x1 = IGetVersions(sparql)
                latest_sparql = x1.latest_version()
                ob = latest_sparql

                if latest_sparql.query_with_comments == query:
                    changed = False

                break

        if not ob:
            _id = generateUniqueId("Sparql")
            _id = self.invokeFactory(type_name="Sparql", id=_id)
            ob = self[_id]
            ob.edit(
                title=title,
                endpoint_url=endpoint,
                sparql_query=query,
            )
            ob._renameAfterCreation(check_auto_id=True)
            ob.invalidateWorkingResult()
        else:
            if changed:
                ob = versions.create_version(ob)
                ob.edit(
                    sparql_query=query,
                )
                ob.invalidateWorkingResult()

        setSecurityManager(oldSecurityManager)

        return ob

    def findQuery(self, title):
        """Find the Query in the bookmarks folder
        """
        ob = None

        for sparql in self.values():
            if sparql.title == title:
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
