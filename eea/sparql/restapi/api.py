from eea.sparql.converter.sparql2json import sparql2json
from plone.restapi.services import Service


class SparqlQueryGET(Service):
    """ Get the available transactions
    """

    def reply(self):
        res = self.context.execute_query()
        json = sparql2json(res)

        return json
