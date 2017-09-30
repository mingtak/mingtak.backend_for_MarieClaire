# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from mingtak.backend.testing import MINGTAK_BACKEND_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that mingtak.backend is properly installed."""

    layer = MINGTAK_BACKEND_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mingtak.backend is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mingtak.backend'))

    def test_browserlayer(self):
        """Test that IMingtakBackendLayer is registered."""
        from mingtak.backend.interfaces import (
            IMingtakBackendLayer)
        from plone.browserlayer import utils
        self.assertIn(IMingtakBackendLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MINGTAK_BACKEND_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mingtak.backend'])

    def test_product_uninstalled(self):
        """Test if mingtak.backend is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mingtak.backend'))

    def test_browserlayer_removed(self):
        """Test that IMingtakBackendLayer is removed."""
        from mingtak.backend.interfaces import \
            IMingtakBackendLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMingtakBackendLayer, utils.registered_layers())
