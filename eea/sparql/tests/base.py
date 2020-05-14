""" Base module for sparql tests
"""

import six.moves.BaseHTTPServer
import threading

import eea.sparql
from eea.sparql.tests.mock_server import PORT
from eea.sparql.tests.mock_server import Handler

#
# Layered testing
#
from plone.testing.zope import installProduct, uninstallProduct
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
# from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE

try:
    from Zope2.App import zcml
    zcml._initialized = 0
except ImportError:
    pass
try:
    from Products.Five import zcml
    zcml._initialized = 0
except ImportError:
    pass


class EEAFixture(PloneSandboxLayer):
    """ EEA Testing Policy
    """
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        self.loadZCML(package=eea.sparql)
        installProduct(app, 'eea.sparql')
        self.server = six.moves.BaseHTTPServer.HTTPServer(("", PORT), Handler)
        self.server_thread = threading.Thread(target=self.server.handle_request)
        self.server_thread.start()

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        uninstallProduct(app, 'eea.sparql')
        self.server.server_close()
        self.server_thread.join()

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        applyProfile(portal, 'eea.sparql:default')

        # Login as manager
        setRoles(portal, TEST_USER_ID, ['Manager'])


EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEASparql:Functional')
