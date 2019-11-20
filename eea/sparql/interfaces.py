""" Sparql interfaces module
"""

from zope import schema
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface

from collective.z3cform.datagridfield import DictRow
from eea.sparql import sparqlMessageFactory as _

from plone.autoform import directives
from plone.supermodel import model
from plone.supermodel.directives import fieldset, primary

from z3c.form.interfaces import IEditForm

class IArgumentsSchema(Interface):
    """ Arguments table schema (arg_spec)
    """

    name = schema.TextLine(title=u"Argument name", required=False)
    query = schema.TextLine(title=u"Argument query", required=False)


class ISparql(Interface):
    """
    """


class ISparqlQuery(model.Schema, ISparql):
    """ISparql"""

    sparql_query = schema.Text(
        title=_(u'Sparql query'),
        required=True
    )

    endpoint_url = schema.URI(
        title=_(u'Sparql endpoint URL'),
        required=True,
        default="https://semantic.eea.europa.eu/sparql"
    )

    timeout = schema.Int(
        title=_(u'Timeout'),
        required=True,
        default=10,
    )

    directives.widget(arg_spec='collective.z3cform.datagridfield.DataGridFieldFactory')
    # primary('arg_spec')
    arg_spec = schema.List(title=_(u'Arguments'), required=False,
                value_type=DictRow(title=u'tablerow', schema=IArgumentsSchema))

    directives.mode(sparql_static='hidden')
    # directives.mode(IEditForm, sparql_static='input') # Display Field on edit
    sparql_static = schema.Bool(
        title=_(u'Static query'), required=False, default=False,
        description="The data will be fetched only once"
    )

    directives.mode(sparql_results='hidden')
    sparql_results = schema.Text(
        title=_(u'Results'),
        required=False
    )




class ISparqlBookmarksFolder(ISparqlQuery):
    """ISparqlBookmarksFolder"""


class ISparqlBookmarksFolderAdded(IObjectEvent):
    """An event signalling that the sparql bookmarks folder was added
    """