import os
import shutil
import unittest
from hedweb.app_factory import AppFactory


def test_dictionaries():
    base_path = os.path.dirname(os.path.abspath(__file__))
    test_dict = {'hed-xml-file': os.path.join(base_path, 'data/HED8.0.0-alpha.1.xml'),
                 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                 'json-path': os.path.join(base_path, 'data/short_form_valid.json'),
                 'json-file': 'short_form_valid.json',
                 'check-for-warnings': True}
    return test_dict


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

    def test_generate_input_from_dictionary_form(self):
        from hedweb.dictionary import generate_input_from_dictionary_form
        self.assertRaises(TypeError, generate_input_from_dictionary_form, {},
                          "An exception should be raised if an empty request is passed")

    def test_dictionary_process_empty_file(self):
        from hedweb.dictionary import dictionary_process
        from hed.util.exceptions import HedFileError
        arguments = {'json-path': ''}
        try:
            dictionary_process(arguments)
        except HedFileError:
            pass
        except Exception:
            self.fail('dictionary_process threw the wrong exception when dictionary-path was empty')
        else:
            self.fail('dictionary_process should have thrown a HedFileError exception when json-path was empty')

    def test_dictionary_process(self):
        from hedweb.dictionary import dictionary_process
        from hedweb.constants import common
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/good_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED 7.1.2.xml',
                     'json-path': json_path, 'json-file': 'good_events.json', 'command': common.COMMAND_TO_SHORT}
        with self.app.app_context():
            response = dictionary_process(arguments)
            headers = dict(response.headers)
            self.assertEqual('warning', headers['Category'],
                             'dictionary_process to short should give warning when JSON with errors')
            self.assertTrue(response.data,
                            'dictionary_process to short should not convert using HED 7.1.2.xml')

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'json-path': json_path, 'json-file': 'good_events.json', 'command': common.COMMAND_TO_SHORT}
        with self.app.app_context():
            response = dictionary_process(arguments)
            headers = dict(response.headers)
            self.assertEqual('success', headers['Category'],
                             'dictionary_process to short should return success if converted')

    def test_dictionary_convert_to_short(self):
        from hedweb.dictionary import dictionary_convert
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/good_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED 7.1.2.xml',
                     'json-path': json_path, 'json-file': 'good_events.json'}
        with self.app.app_context():
            results = dictionary_convert(arguments, short_to_long=False)
            self.assertTrue(results['file_name'],
                            'dictionary_convert to long results should have file_name key')
            self.assertEqual('warning', results["category"],
                             'dictionary_convert to long category should be warning for errors')

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'json-path': json_path, 'json-file': 'good_events.json'}
        with self.app.app_context():
            results = dictionary_convert(arguments, short_to_long=False)
            self.assertTrue(results['file_name'],
                            'dictionary_convert to long results should have file_name key')
            self.assertEqual('success', results["category"],
                             'dictionary_convert to long category should be success when no errors')

    def test_dictionary_convert_to_short(self):
        from hedweb.dictionary import dictionary_convert
        from hedweb.constants import common
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/good_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED 7.1.2.xml',
                     'json-path': json_path, 'json-file': 'good_events.json', 'command': common.COMMAND}
        with self.app.app_context():
            results = dictionary_convert(arguments)
            self.assertTrue(results["file_name"], "dictionary_convert results should have file_name key")
            self.assertEqual('warning', results["category"],
                             'dictionary_convert category should be warning for errors')

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'json-path': json_path, 'json-file': 'good_events.json'}
        with self.app.app_context():
            results = dictionary_convert(arguments)
            self.assertTrue(results["file_name"], "dictionary_convert results should have file_name key")
            self.assertEqual('success', results["category"],
                             'dictionary_convert category should be success when no errors')

    def test_dictionary_validate(self):
        from hedweb.dictionary import dictionary_validate
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/good_events.json')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED7.1.2.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED 7.1.2.xml',
                     'json-path': json_path, 'json-file': 'good_events.json'}
        with self.app.app_context():
            results = dictionary_validate(arguments)
            self.assertTrue(results["file_name"],
                             'dictionary_validate results should have a file_name key when validation errors')
            self.assertEqual('warning', results["category"],
                             'dictionary_validate category should be warning when errors')

        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0-alpha.1.xml')
        arguments = {'hed-xml-file': schema_path, 'hed-display-name': 'HED8.0.0-alpha.1.xml',
                     'json-path': json_path, 'json-file': 'good_events.json'}
        with self.app.app_context():
            results = dictionary_validate(arguments)
            self.assertFalse("file_name" in results,
                             'dictionary_validate results should not have a file_name key when no validation errors')
            self.assertEqual('success', results["category"],
                             'dictionary_validate category should be success when no errors')


if __name__ == '__main__':
    unittest.main()
