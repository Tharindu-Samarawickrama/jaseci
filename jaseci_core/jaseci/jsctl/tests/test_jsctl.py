from unittest import TestCase
from jaseci.utils.utils import TestCaseHelper
from jaseci.jsctl import jsctl
from click.testing import CliRunner
import json


class jsctl_test(TestCaseHelper, TestCase):
    """Unit tests for Jac language"""

    def setUp(self):
        super().setUp()
        self.call("app load -name zsb -code jaseci/jsctl/tests/zsb.jac")

    def call(self, cmd):
        runner = CliRunner()
        return runner.invoke(jsctl.cli,
                             ["-m"]+cmd.split(' ')).output

    def call_cast(self, cmd):
        return json.loads(self.call(cmd))

    def tearDown(self):
        jsctl.session["master"]._h.clear_mem_cache()
        super().tearDown()

    def test_jsctl_extract_tree(self):
        out = jsctl.extract_api_tree()
        self.assertIn("create", out)
        self.assertIn("get", out)
        self.assertIn("load", out)
        self.assertIn("set", out)
        self.assertIn("config", out)
        self.assertNotIn("jadc", out)

    def test_help_screen(self):
        r = self.call('--help')
        self.assertIn('Specify filename', r)
        self.assertIn("Group of `list` commands", r)
        r = self.call('get --help')
        self.assertIn("Group of `get node` commands", r)

    def test_jsctl_create_graph_mem_only(self):
        r = self.call('create graph -name test')
        self.assertIn('test', r)
        r = self.call('list graph')
        self.assertIn('test', r)

    def test_jsctl_load_app(self):
        r = self.call('list graph')
        self.assertIn('zsb', r)

    def test_jsctl_aliases(self):
        """Tests that alias mapping api works"""
        gph_id = self.call_cast('list graph')[0]['jid']
        snt_id = self.call_cast('list sentinel')[0]['jid']
        self.call(f'create alias -name s -value {snt_id}')
        self.call(f'create alias -name g -value {gph_id}')
        self.assertEqual(len(self.call_cast('get graph -gph g')), 1)
        self.call(f'prime run -snt s -nd g -name init')
        self.assertEqual(len(self.call_cast('get graph -gph g')), 2)
        self.call(f'alias delete -all true')
        self.assertEqual(len(self.call_cast(f'alias list').keys()), 0)

    def test_jsctl_config_cmds(self):
        """Tests that config commands works"""
        self.call(f'config set -name APPLE -value TEST -do_check False')
        self.call(f'config set -name APPLE -value Grape2 -do_check False')
        self.call(f'config set -name "Banana" -value "Grape" -do_check False')
        self.call(f'config set -name "Pear" -value "Banana" -do_check False')
        r = self.call_cast('config get -name APPLE')
        self.assertEqual(r, 'Grape2')
        r = self.call_cast('config list')
        self.assertEqual(len(r), 3)

    def test_jsctl_default_snt_setting(self):
        """Tests that alias mapping api works"""
        self.logger_on()
        snt_id = self.call_cast('list sentinel')[0]['jid']
        self.call(f'sentinel active set -snt {snt_id}')
        self.call(f'sentinel active get')
        self.assertEqual(len(self.call_cast(f'walker list')), 21)

    def test_jsctl_master_defaults(self):
        """Tests that alias mapping api works"""
        gph_id = self.call_cast('graph list')[0]['jid']
        snt_id = self.call_cast('sentinel list')[0]['jid']
        self.call(f'sentinel active set -snt {snt_id}')
        self.call(f'graph active set -gph {gph_id}')
        self.assertEqual(len(self.call_cast('graph get')), 1)
        self.call(f'walker primerun -name init')
        self.assertEqual(len(self.call_cast('graph get')), 2)
