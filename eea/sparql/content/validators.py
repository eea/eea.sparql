""" Custom AT Validators
"""
from Products.statusmessages.interfaces import IStatusMessage
from Products.validation.interfaces.IValidator import IValidator
from zope.annotation import IAnnotations
from zope.interface import implements

from Products.ZSPARQLMethod.Method import run_with_timeout
from Products.ZSPARQLMethod.Method import query_and_get_result


class SparqlQueryValidator(object):
    """ Validator
    """
    implements(IValidator)

    def __init__(self, name, title='Sparql Query result size',
                 description='Check if sparql_query result is too big'):
        self.name = name
        self.title = title or name
        self.description = description

    def run_query(self, request, func, spec):
        """
        :param request: Object request
        :type request: object
        :param func: query_and_get_result funcion used to query Sparql
        :type func: function
        :param spec: Endpoint url and sparql query
        :type spec: tuple
        :return: Dict with Sparql results
        :rtype: dict
        """
        cache = IAnnotations(request)
        key = 'query_result'
        data = cache.get('query_result', None)
        if data is None:
            data = run_with_timeout(15, func, *spec)
            cache[key] = data
        return data

    def __call__(self, value, *args, **kwargs):
        """ Check if provided query is within size limit """
        obj = kwargs.get('instance')
        request = kwargs['REQUEST']
        if 'atct_edit' not in request.URL0:
            return 1

        arg_spec = (obj.endpoint_url, value)
        results = self.run_query(request, query_and_get_result, arg_spec)
        results_len = len(results.get('result', {}).get('rows', {}))
        pprop = obj.portal_properties
        site_props = getattr(pprop, 'site_properties', None)
        max_rows = site_props.getProperty('sparql_max_row_length', 9000)
        sparql_msg = site_props.getProperty('sparql_max_row_msg', "%s %s")
        msg = sparql_msg % (results_len, max_rows)
        if results_len > max_rows:
            IStatusMessage(request).addStatusMessage(str(msg),
                                                     type='warning')
            return 1
        return 1

