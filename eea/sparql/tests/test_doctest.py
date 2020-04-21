""" Test doctests module
"""

import unittest
import doctest

from Testing import ZopeTestCase as ztc

from eea.sparql.tests import base
from plone.testing import layered



def test_suite():
    """ Suite
    """
    # return unittest.TestSuite([

    #     ztc.ZopeDocFileSuite(
    #         'converter/sparql2json.py', package='eea.sparql',
    #         test_class=base.SparqlFunctionalTestCaseLayer,
    #         optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
    #             doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),


    #     ])

    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                'converter/sparql2json.py',
                optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                package='eea.sparql'),
            layer=base.FUNCTIONAL_TESTING),
    ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
