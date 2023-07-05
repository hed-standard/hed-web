import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase


class Test(TestWebBase):
    def test_generate_input_from_schema_form_empty(self):
        from hedweb.schema import get_input_from_form
        self.assertRaises(TypeError, get_input_from_form, {},
                          "An exception is raised if an empty request is passed to generate_input_from_schema")

    def test_get_input_from_schema_form_valid(self):
        from hedweb.constants import base_constants
        from hedweb.schema import get_input_from_form
        with self.app.test:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
            with open(schema_path, 'rb') as fp:
                environ = create_environ(data={base_constants.SCHEMA_FILE: fp,
                                               base_constants.SCHEMA_UPLOAD_OPTIONS: base_constants.SCHEMA_FILE_OPTION,
                                               base_constants.COMMAND_OPTION:  base_constants.COMMAND_CONVERT_SCHEMA})
            request = Request(environ)
            arguments = get_input_from_form(request)
            self.assertIsInstance(arguments[base_constants.SCHEMA_STRING], str,
                                  "get_input_from_form should have a HED schema")
            self.assertEqual(base_constants.COMMAND_CONVERT_SCHEMA, arguments[base_constants.COMMAND],
                             "get_input_from_form should have a command")
            self.assertFalse(arguments[base_constants.CHECK_FOR_WARNINGS],
                             "get_input_from_form should have check_warnings false when not given")

    def test_schema_process(self):
        from hedweb.schema import process
        from hed.errors.exceptions import HedFileError
        arguments = {'schema_path': ''}
        with self.assertRaises(HedFileError):
            process(arguments)

    def test_schema_check(self):
        from hedweb.schema import schema_validate
        from hed import schema as hedschema
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        display_name = 'HED8.0.0.xml'
        with self.app.app_context():
            results = schema_validate(hed_schema, display_name)
            self.assertTrue(results['data'], "HED 8.0.0 is not fully HED-3G compliant")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.1.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        display_name = 'HED8.1.0.xml'
        with self.app.app_context():
            results = schema_validate(hed_schema, display_name)
            self.assertFalse(results['data'], "HED8.0.0 is HED-3G compliant")

    def test_schema_convert(self):
        from hedweb.schema import schema_convert
        from hed import schema as hedschema
        from hed.errors.exceptions import HedFileError

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        display_name = 'HED8.0.0.4.xml'
        with self.app.app_context():
            results = schema_convert(hed_schema, display_name)
            self.assertTrue(results['data'], "HED 8.0.0.xml can be converted to mediawiki")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HEDbad.xml')
        display_name = 'HEDbad.xml'
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                hed_schema = hedschema.load_schema(schema_path)
                schema_convert(hed_schema, display_name)


if __name__ == '__main__':
    unittest.main()
