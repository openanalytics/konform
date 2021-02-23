from unittest import TestCase
from konform import Konform


class TestKonform(TestCase):
    def test_check_kind(self):
        runner = Konform()
        runner._check_kind({}, "")
        self.assertEqual(runner._problems, 1)
        runner._check_kind({"kind": "Deployment"}, "test.service.yaml")
        self.assertEqual(runner._problems, 2)
        runner._check_kind({"kind": "Deployment"}, "test.deployment.yaml")
        self.assertEqual(runner._problems, 2)
        