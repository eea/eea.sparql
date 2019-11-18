"""Definition of the SparqlBookmarks content type
"""

import logging
from random import random

# import pytz
# , SpecialUsers, getSecurityManager
# from AccessControl.SecurityManagement import (newSecurityManager,
#                                               setSecurityManager)
# from eea.sparql.converter.sparql2json import sparql2json
# import cPickle
# import datetime
# from eea.sparql.events import SparqlBookmarksFolderAdded
# from eea.sparql.interfaces import ISparql, ISparqlBookmarksFolder
# from eea.versions import versions
# from eea.versions.interfaces import IGetVersions, IVersionEnhanced
# from plone.app.blob.field import BlobField
# from Products.Archetypes import atapi
# from Products.Archetypes.atapi import (BooleanField, BooleanWidget,
#                                        IntegerField, Schema, SelectionWidget,
#                                        StringField, StringWidget,
#                                        TextAreaWidget, TextField)
# from Products.ATContentTypes.content import base, schemata
# from Products.ATContentTypes.content.folder import ATFolder
# from Products.CMFCore.utils import getToolByName
# from Products.CMFEditions.interfaces.IModifier import \
#     FileTooLargeToVersionError
# from Products.DataGridField import DataGridField, DataGridWidget
# from Products.DataGridField.Column import Column
# from Products.DataGridField.LinesColumn import LinesColumn
# from eea.sparql.async import IAsyncService
# from ZODB.POSException import POSKeyError
# from zope.component import queryUtility
# from zope.event import notify
from zope.interface import implementer

import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from eea.sparql.cache import cacheSparqlKey, ramcache  # cacheSparqlMethodKey,
from eea.sparql.interfaces import ISparqlQuery
from plone.dexterity.content import Container
from Products.ZSPARQLMethod.Method import (QueryTimeout, ZSPARQLMethod,
                                           interpolate_query, map_arg_values,
                                           parse_arg_spec,
                                           query_and_get_result,
                                           raw_query_and_get_result,
                                           run_with_timeout)
from eea.sparql.content.sparqlquery import generateUniqueId



# class SparqlBookmarksFolder(ATFolder, Sparql):
#     """Sparql Bookmarks Folder"""
#     implements(ISparqlBookmarksFolder)
#     meta_type = "SparqlBookmarksFolder"
#     schema = SparqlBookmarksFolderSchema
#
#     def checkQuery(self, title, endpoint, query):
#         """Check if a query already exists
#            0 - missing
#            1 - exists
#            2 - exists but changed"""
#         found = False
#         changed = True
#
#         for sparql in self.values():
#             if sparql.title == title.encode('utf8'):
#                 latest_sparql = IGetVersions(sparql).latest_version()
#                 found = True
#
#                 if latest_sparql.query_with_comments == query:
#                     changed = False
#
#                 break
#
#         if not found:
#             return 0
#
#         if not changed:
#             return 1
#
#         return 2
#
#     def addOrUpdateQuery(self, title, endpoint, query):
#         """Update an already existing query
#            Create new version"""
#         oldSecurityManager = getSecurityManager()
#         newSecurityManager(None, SpecialUsers.system)
#
#         ob = None
#
#         changed = True
#
#         for sparql in self.values():
#             if sparql.title == title:
#                 x1 = IGetVersions(sparql)
#                 latest_sparql = x1.latest_version()
#                 ob = latest_sparql
#
#                 if latest_sparql.query_with_comments == query:
#                     changed = False
#
#                 break
#
#         if not ob:
#             _id = generateUniqueId("Sparql")
#             _id = self.invokeFactory(type_name="Sparql", id=_id)
#             ob = self[_id]
#             ob.edit(
#                 title=title,
#                 endpoint_url=endpoint,
#                 sparql_query=query,
#             )
#             ob._renameAfterCreation(check_auto_id=True)
#             ob.invalidateWorkingResult()
#         else:
#             if changed:
#                 ob = versions.create_version(ob)
#                 ob.edit(
#                     sparql_query=query,
#                 )
#                 ob.invalidateWorkingResult()
#
#         setSecurityManager(oldSecurityManager)
#
#         return ob
#
#     def findQuery(self, title):
#         """Find the Query in the bookmarks folder
#         """
#         ob = None
#
#         for sparql in self.values():
#             if sparql.title == title:
#                 latest_sparql = IGetVersions(sparql).latest_version()
#                 ob = latest_sparql
#
#                 break
#
#         return ob
#
#     def syncQueries(self):
#         """sync all queries from bookmarks"""
#         queries = self.execute().get('result', {}).get('rows', {})
#
#         for query in queries:
#             query_name = query[0].value
#             query_sparql = query[2].value
#             self.addOrUpdateQuery(query_name,
#                                   self.endpoint_url,
#                                   query_sparql)
