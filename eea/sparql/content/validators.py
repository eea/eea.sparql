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
        :param request:
        :type request:
        :param func:
        :type func:
        :param spec:
        :type spec:
        :return:
        :rtype:
        """
        cache = IAnnotations(request)
        key = 'query_result'
        data = cache.get('query_result', None)
        if data is not None:
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
        if results_len > 9000:
            msg = "The query result is too large given that there " \
                  "are %s rows" % results_len
            IStatusMessage(request).addStatusMessage(str(msg),
                                                     type='warning')
            return 1
        return 1

