import logging

from eea.sparql.converter.sparql2json import sparql2json
from plone.restapi.services import Service

logger = logging.getLogger('eea.sparql.restapi')


class SparqlQueryGET(Service):
    """ Get the available transactions
    In order to test the service you need to send a request to the url
    https://github.com/plone/plone.rest#content-negotiation
    """

    def reply(self):
        res = self.context.execute_query()

        if 'exception' in res:
            logger.warning('Could not retrieve data from sparql endpoint')

            return {}

        json = sparql2json(res)

        return json
