import os
import shutil
import unittest
from flask import Response
from hedweb.app_factory import AppFactory
from hedweb.constants import common


def event_input():
    base_path = os.path.dirname(os.path.abspath(__file__))
    test_events = {common.HED_XML_FILE: os.path.join(base_path, 'data/HED8.0.0-alpha.1.xml'),
                   common.HED_DISPLAY_NAME: 'HED8.0.0-alpha.1.xml',
                   common.JSON_PATH: os.path.join(base_path, 'data/short_form_valid.json'),
                   common.JSON_FILE: 'short_form_valid.json',
                   common.SPREADSHEET_PATH: os.path.join(base_path, 'data/ExcelMultipleSheets.xlsx'),
                   common.SPREADSHEET_FILE: 'ExcelMultipleSheets.xlsx',
                   common.WORKSHEET_NAME: 'LKT Events',
                   common.HAS_COLUMN_NAMES: True,
                   common.CHECK_FOR_WARNINGS: True
                   }
    return test_events


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/upload')
        app = AppFactory.create_app('config.TestConfig')
        with app.app_context():
            from hedweb.routes import route_blueprint
            app.register_blueprint(route_blueprint)
            if not os.path.exists(cls.upload_directory):
                os.mkdir(cls.upload_directory)
            app.config['UPLOAD_FOLDER'] = cls.upload_directory
            cls.app = app
            cls.app.test = app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.upload_directory)

    def test_generate_input_from_events_form(self):
        self.assertTrue(1, "Testing generate_input_from_events_form")

    def test_events_process(self):
        from hedweb.events import events_process
        from hed.util.exceptions import HedFileError
        # Test for empty events-path
        arguments = {'events-path': ''}
        try:
            events_process(arguments)
        except HedFileError:
            pass
        except Exception:
            self.fail('events_process threw the wrong exception when events-path was empty')
        else:
            self.fail('events_process should have thrown a HedFileError exception when events-path was empty')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'events-path': events_path, 'hed-option-validate': True,
                     'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml'}
        result = events_process(arguments)
        self.assertTrue(isinstance(result, Response), "Validation should return a response object")

    def test_events_assemble(self):
        from hedweb.events import events_assemble
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')

        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'events-path': events_path, 'events-file': 'bids_events.tsv',
                     'json-path': json_path, 'json-file': 'bids_events.json', 'hed-option-assemble': True}
        with self.app.app_context():
            response = events_assemble(arguments)
            headers = dict(response.headers)
            self.assertEqual('success', headers['Category'],
                             "events_assemble should assemble with 8.0.0-alpha.1")
            self.assertTrue(response.data, "events_assemble should have response data when assembly is successful")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED7.1.2.xml',
                     'events-path': events_path, 'events-file': 'bids_events.tsv', 'json-path': json_path,
                     'json-file': 'bids_events.json', 'hed-option-assemble': True}
        with self.app.app_context():
            response = events_assemble(arguments)
            headers = dict(response.headers)
            self.assertEqual('warning', headers['Category'],
                             "events_assemble should return validation errors for bids_events.json with 7.1.2")
            self.assertTrue(response.data, "events_assemble should return response data for validation errors")

    def test_events_validate(self):
        from hedweb.events import events_validate
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')

        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED7.1.2.xml',
                     'events-path': events_path, 'events-file': 'bids_events.tsv',
                     'json-path': json_path, 'json-file': 'bids_events.json', 'hed-option-validate': True}

        with self.app.app_context():
            response = events_validate(arguments)
            headers = dict(response.headers)
            self.assertEqual('warning', headers['Category'],
                             "events_validate should return validation errors for bids_events.json with 7.1.2")
            self.assertTrue(response.data, "events_validate should return response data for validation errors")

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'events-path': events_path, 'events-file': 'bids_events.tsv', 'json-path': json_path,
                     'json-file': 'bids_events.json', 'hed-option-validate': True}
        with self.app.app_context():
            response = events_validate(arguments)
            headers = dict(response.headers)
            self.assertEqual('success', headers['Category'],
                             "events_validate should validate bids_events.json with 8.0.0-alpha.1")
            self.assertFalse(response.data, "events_validation should have no response data for successful validation")


if __name__ == '__main__':
    unittest.main()
