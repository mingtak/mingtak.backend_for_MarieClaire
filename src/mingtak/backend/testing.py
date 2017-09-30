# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import mingtak.backend


class MingtakBackendLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=mingtak.backend)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'mingtak.backend:default')


MINGTAK_BACKEND_FIXTURE = MingtakBackendLayer()


MINGTAK_BACKEND_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MINGTAK_BACKEND_FIXTURE,),
    name='MingtakBackendLayer:IntegrationTesting'
)


MINGTAK_BACKEND_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MINGTAK_BACKEND_FIXTURE,),
    name='MingtakBackendLayer:FunctionalTesting'
)


MINGTAK_BACKEND_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MINGTAK_BACKEND_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MingtakBackendLayer:AcceptanceTesting'
)
