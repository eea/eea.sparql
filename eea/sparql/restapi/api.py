from eea.sparql.converter.sparql2json import sparql2json
from plone.restapi.services import Service


class SparqlQueryGET(Service):
    """ Get the available transactions
    In order to test the service you need to make send a request to the url
    https://github.com/plone/plone.rest#content-negotiation
    """

    def reply(self):
        res = self.context.execute_query()
        json = sparql2json(res)

        return json
