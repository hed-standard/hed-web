import os
import unittest

from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
import hed.schema as hedschema
from hed import models
from hedweb.constants import base_constants


class Test(TestWebBase):
    def test_generate_input_from_sidecar_form_empty(self):
        from hedweb.sidecars import get_input_from_form
        self.assertRaises(TypeError, get_input_from_form, {},
                          "An exception should be raised if an empty request is passed")

    def test_generate_input_from_sidecars_form(self):
        from hed.models import Sidecar
        from hed.schema import HedSchema
        from hedweb.sidecars import get_input_from_form
        with self.app.test:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            with open(sidecar_path, 'rb') as fp:
                environ = create_environ(data={base_constants.SIDECAR_FILE: fp, base_constants.SCHEMA_VERSION: '8.0.0',
                                               base_constants.COMMAND_OPTION: base_constants.COMMAND_TO_LONG})
            request = Request(environ)
            arguments = get_input_from_form(request)

            self.assertIsInstance(arguments[base_constants.SIDECAR], Sidecar,
                                  "generate_input_from_sidecar_form should have a JSON dictionary in sidecar list")
            self.assertIsInstance(arguments[base_constants.SCHEMA], HedSchema,
                                  "generate_input_from_sidecar_form should have a HED schema")
            self.assertEqual(base_constants.COMMAND_TO_LONG, arguments[base_constants.COMMAND],
                             "generate_input_from_sidecar_form should have a command")
            self.assertFalse(arguments[base_constants.CHECK_FOR_WARNINGS],
                             "generate_input_from_sidecar_form should have check for warnings false when not given")

    def test_sidecars_process_empty_file(self):
        from hedweb.sidecars import process
        from hed.errors.exceptions import HedFileError
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                arguments = {'sidecar_path': ''}
                process(arguments)

    def test_sidecars_process_invalid(self):
        from hedweb.sidecars import process
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        json_sidecar = models.Sidecar(files=sidecar_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)

        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events_bad',
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'],
                             'process to short should give warning when JSON with errors')
            self.assertTrue(results['data'],
                            'process to short should not convert using HED 8.0.0.xml')

    def test_sidecars_process_invalid_v2(self):
        from hedweb.sidecars import process
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events_errors.json')
        json_sidecar = models.Sidecar(files=sidecar_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)

        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events_bad',
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'],
                             'process to short should give warning when JSON with errors')
            self.assertTrue(results['data'],
                            'process to short should not convert using HED 8.0.0.xml')

    def test_sidecars_process_valid_to_short(self):
        from hedweb.sidecars import process
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events',
                     base_constants.EXPAND_DEFS: False,
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}

        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process to short should return success if no errors')

    def test_sidecars_process_valid_to_short_defs_expanded(self):
        from hedweb.sidecars import process
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events',
                     base_constants.EXPAND_DEFS: True,
                     base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}

        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to short should return a dict when no errors and defs expanded')
            self.assertEqual('success', results['msg_category'],
                             'process to short should return success if no errors and defs_expanded')

    def test_sidecars_process_valid_to_long(self):
        from hedweb.sidecars import process
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events',
                     base_constants.EXPAND_DEFS: False,
                     base_constants.COMMAND: base_constants.COMMAND_TO_LONG}

        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to long should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process to long should return success when no errors')

    def test_sidecars_process_valid_to_long_defs_expanded(self):
        from hedweb.sidecars import process
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SIDECAR: json_sidecar,
                     base_constants.SIDECAR_DISPLAY_NAME: 'bids_events',
                     base_constants.EXPAND_DEFS: True,
                     base_constants.COMMAND: base_constants.COMMAND_TO_LONG}

        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process to long should return a dict when no errors and defs expanded')
            self.assertEqual('success', results['msg_category'],
                             'process to long should return success if converted when no errors and defs expanded')

    def test_sidecars_convert_to_long_invalid(self):
        from hed import models
        from hedweb.sidecars import sidecar_convert
        from hedweb.constants import base_constants
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        options = {base_constants.COMMAND: base_constants.COMMAND_TO_LONG}
        with self.app.app_context():
            results = sidecar_convert(hed_schema, json_sidecar, options)
            self.assertTrue(results['data'],
                            'sidecar_convert to long results should have data key')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_convert to long msg_category should be warning for errors')

    def test_sidecars_convert_to_long_valid(self):
        from hed import models
        from hedweb.sidecars import sidecar_convert
        from hedweb.constants import base_constants
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        options = {base_constants.COMMAND: base_constants.COMMAND_TO_LONG}
        with self.app.app_context():
            results = sidecar_convert(hed_schema, json_sidecar, options)
            self.assertTrue(results['data'],
                            'sidecar_convert to long results should have data key')
            self.assertEqual('success', results["msg_category"],
                             'sidecar_convert to long msg_category should be success when no errors')

    def test_sidecars_convert_to_short_invalid(self):
        from hed import models
        from hedweb.sidecars import sidecar_convert
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        options = {base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            results = sidecar_convert(hed_schema, json_sidecar, options)
            self.assertTrue(results['data'], 'sidecar_convert results should have data key')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_convert msg_category should be warning for errors')

    def test_bad_sidecar(self):
        from hed import models
        from hed.schema import load_schema_version
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/both_types_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events_bad')
        hed_schema = load_schema_version('8.1.0')
        issues = json_sidecar.validate(hed_schema)
        self.assertIsInstance(issues, list)
        self.assertEqual(len(issues), 16)

    def test_sidecars_convert_to_short_valid(self):
        from hed import models
        from hedweb.sidecars import sidecar_convert
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        options = {base_constants.COMMAND: base_constants.COMMAND_TO_SHORT}
        with self.app.app_context():
            results = sidecar_convert(hed_schema, json_sidecar, options)
            self.assertTrue(results['data'], 'sidecar_convert results should have data key')
            self.assertEqual('success', results['msg_category'],
                             'sidecar_convert msg_category should be success when no errors')

    def test_sidecars_validate_invalid(self):
        from hed import models
        from hedweb.sidecars import sidecar_validate
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        with self.app.app_context():
            results = sidecar_validate(hed_schema, json_sidecar)
            self.assertTrue(results['data'],
                            'sidecar_validate results should have a data key when validation issues')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_validate msg_category should be warning when errors')

    def test_sidecars_validate_invalid_multiple(self):
        from hed import models
        from hedweb.sidecars import sidecar_validate
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events_bad.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events_bad')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        with self.app.app_context():
            results = sidecar_validate(hed_schema, json_sidecar)
            self.assertTrue(results['data'],
                            'sidecar_validate results should have a data key when validation issues')
            self.assertEqual('warning', results['msg_category'],
                             'sidecar_validate msg_category should be warning when errors')

    def test_sidecars_validate_valid(self):
        from hed import models
        from hedweb.sidecars import sidecar_validate
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        json_sidecar = models.Sidecar(files=json_path, name='bids_events')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        with self.app.app_context():
            results = sidecar_validate(hed_schema, json_sidecar)
            self.assertFalse(results['data'],
                             'sidecar_validate results should not have a data key when no validation issues')
            self.assertEqual('success', results["msg_category"],
                             'sidecar_validate msg_category should be success when no issues')


if __name__ == '__main__':
    unittest.main()
