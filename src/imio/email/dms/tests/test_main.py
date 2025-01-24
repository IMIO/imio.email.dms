from imio.email.dms.main import modify_attachments
from imio.email.parser.parser import Parser
from imio.email.parser.tests.test_parser import get_eml_message

import unittest


class TestMain(unittest.TestCase):
    def test_modify_attachments(self):
        to_tests = [
            {
                "fn": "01_email_with_inline_and_annexes.eml",
                "orig": {"nb": 4, "len": [269865, 673, 9309, 310852]},
                "mod": {"all_nb": 4, "at_nb": 2, "len": [186946, 673, 9309, 154746], "mod": [True, None, None, True]},
            },
        ]
        # breakpoint()
        for dic in to_tests:
            name = dic["fn"]
            eml = get_eml_message(name)
            parser = Parser(eml, False, name)
            self.assertEqual(len(parser.attachments), dic["orig"]["nb"])
            self.assertListEqual([at["len"] for at in parser.attachments], dic["orig"]["len"])
            mod_attach = modify_attachments(name, parser.attachments)
            self.assertEqual(len(mod_attach), dic["mod"]["all_nb"])
            self.assertListEqual([at["len"] for at in mod_attach], dic["mod"]["len"])
            self.assertListEqual([at.get("modified") for at in mod_attach], dic["mod"]["mod"])
            mod_attach = modify_attachments(name, parser.attachments, with_inline=False)
            self.assertEqual(len(mod_attach), dic["mod"]["at_nb"])
