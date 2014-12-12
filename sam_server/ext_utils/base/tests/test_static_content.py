from django.test import TestCase

from ..static_content import rewrite_package_path


class StaticContentTests(TestCase):
    def test_rewrite_path(self):
        ## Should return a top level /packages path
        path = '/assets/packages/cs_elements/qrcode/qrcode.html'
        self.assertEquals(
            rewrite_package_path(path),
            '/packages/cs_elements/qrcode/qrcode.html'
        )

        ## Should unquote urlescaped chars
        path = '/assets/packages/cs%20elements/qrcode/qrcode.html'
        self.assertEquals(
            rewrite_package_path(path),
            '/packages/cs elements/qrcode/qrcode.html'
        )
        ## Should return non-package paths unchanged
        path = '/assets/cs_elements/qrcode/qrcode.html'
        self.assertEquals(rewrite_package_path(path), path)
