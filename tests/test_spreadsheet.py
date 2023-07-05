import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request
from tests.test_web_base import TestWebBase
import hed.schema as hedschema
from hed.models import SpreadsheetInput
from hedweb.constants import base_constants


class Test(TestWebBase):
    def test_get_input_from_spreadsheet_form_empty(self):
        from hedweb.spreadsheet import get_input_from_form
        self.assertRaises(TypeError, get_input_from_form, {},
                          "An exception is raised if an empty request is passed to generate_input_from_spreadsheet")

    def test_get_input_from_spreadsheet_form(self):
        from hed.models import SpreadsheetInput
        from hed.schema import HedSchema
        from hedweb.spreadsheet import get_input_from_form
        with self.app.test:
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelOneSheet.xlsx')
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
            with open(spreadsheet_path, 'rb') as fp:
                with open(schema_path, 'rb') as sp:
                    environ = create_environ(data={base_constants.SPREADSHEET_FILE: fp,
                                                   base_constants.SCHEMA_VERSION: base_constants.OTHER_VERSION_OPTION,
                                                   base_constants.SCHEMA_PATH: sp,
                                                   'column_4_check': 'on', 'column_4_input': '',
                                                   base_constants.WORKSHEET_SELECTED: 'LKT 8HED3',
                                                   base_constants.HAS_COLUMN_NAMES: 'on',
                                                   base_constants.COMMAND_OPTION: base_constants.COMMAND_VALIDATE})

            request = Request(environ)
            arguments = get_input_from_form(request)
            self.assertIsInstance(arguments[base_constants.SPREADSHEET], SpreadsheetInput,
                                  "generate_input_from_spreadsheet_form should have an events object")
            self.assertIsInstance(arguments[base_constants.SCHEMA], HedSchema,
                                  "generate_input_from_spreadsheet_form should have a HED schema")
            self.assertEqual(base_constants.COMMAND_VALIDATE, arguments[base_constants.COMMAND],
                             "generate_input_from_spreadsheet_form should have a command")
            self.assertEqual('LKT 8HED3', arguments[base_constants.WORKSHEET_NAME],
                             "generate_input_from_spreadsheet_form should have a sheet_name name")
            self.assertTrue(arguments[base_constants.HAS_COLUMN_NAMES],
                            "generate_input_from_spreadsheet_form should have column names")

    def test_process_empty_file(self):
        from hedweb.constants import base_constants
        from hedweb.spreadsheet import process
        from hed.errors.exceptions import HedFileError
        arguments = {base_constants.SPREADSHEET: None}
        with self.assertRaises(HedFileError):
            process(arguments)

    def test_spreadsheet_process_validate_invalid(self):
        from hedweb.spreadsheet import process
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        prefix_dict = {2: "Event/Long name/", 1: "Event/Label/", 3: "Event/Description/"}
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT Events',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict, name=spreadsheet_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SPREADSHEET: spreadsheet,
                     base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                     base_constants.CHECK_FOR_WARNINGS: True}
        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process validate should return a dictionary when errors')
            self.assertEqual('warning', results['msg_category'],
                             'process validate should give warning when spreadsheet has errors')
            self.assertTrue(results['data'],
                            'process validate should return validation issues using HED 8.0.0-beta.1')

    def test_process_validate_valid(self):
        from hedweb.spreadsheet import process
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        prefix_dict = {1: "Property/Informational-property/Label/", 3: "Property/Informational-property/Description/"}
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT 8HED3A',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict, name=spreadsheet_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SPREADSHEET: spreadsheet,
                     base_constants.COMMAND: base_constants.COMMAND_VALIDATE,
                     base_constants.CHECK_FOR_WARNINGS: True}
        arguments[base_constants.SCHEMA] = hed_schema

        with self.app.app_context():
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process should return success if validated')

    def test_convert_to_long_excel(self):
        from hedweb.spreadsheet import spreadsheet_convert
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        prefix_dict = {1: "Label/", 3: "Description/"}
        options = {base_constants.COMMAND: base_constants.COMMAND_TO_LONG}
        hed_schema = hedschema.load_schema(schema_path)
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT 8HED3A',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict, name=spreadsheet_path)
        with self.app.app_context():
            tags1 = spreadsheet.dataframe.iloc[0, 4]
            results = spreadsheet_convert(hed_schema, spreadsheet, options=options)
            print(results['data'])
            tags2 = results['spreadsheet'].dataframe.iloc[0, 4]
            self.assertGreater(len(tags2), len(tags1))
            # hed1 = HedString(tags1, hed_schema=hed_schema)
            # hed2 = HedString(tags2, hed_schema=hed_schema)
            self.assertFalse(results['data'],
                             'spreadsheet_convert_to_long results should not have a data key')

            self.assertEqual('success', results["msg_category"],
                             'spreadsheet_validate msg_category should be success when no errors')

    def test_process_convert_to_long(self):
        from hedweb.spreadsheet import process
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT 8HED3A',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=None, name=spreadsheet_path)
        arguments = {base_constants.SCHEMA: hed_schema, base_constants.SPREADSHEET: spreadsheet,
                     base_constants.COMMAND: base_constants.COMMAND_TO_LONG,
                     base_constants.CHECK_FOR_WARNINGS: False}
        arguments[base_constants.SCHEMA] = hed_schema

        with self.app.app_context():
            tags1 = arguments['spreadsheet'].dataframe.iloc[0, 4]
            results = process(arguments)
            self.assertTrue(isinstance(results, dict),
                            'process should return a dict when no errors')
            self.assertEqual('success', results['msg_category'],
                             'process should return success if validated')
            tags2 = results['spreadsheet'].dataframe.iloc[0, 4]
            self.assertGreater(len(tags2), len(tags1))

    def test_validate_valid_excel(self):
        from hedweb.spreadsheet import spreadsheet_validate
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        prefix_dict = {1: "Property/Informational-property/Label/", 3: "Property/Informational-property/Description/"}
        hed_schema = hedschema.load_schema(schema_path)
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT 8HED3A',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict, name=spreadsheet_path)
        with self.app.app_context():
            results = spreadsheet_validate(hed_schema, spreadsheet)
            print(results['data'])
            self.assertFalse(results['data'],
                             'spreadsheet_validate results should not have a data key when no validation issues')
            self.assertEqual('success', results["msg_category"],
                             'spreadsheet_validate msg_category should be success when no errors')

    def test_validate_valid_excel1(self):
        from hedweb.spreadsheet import spreadsheet_validate
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.1.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        prefix_dict = {1: "Property/Informational-property/Label/", 3: "Property/Informational-property/Description/"}
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT 8HED3',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict,
                                       name=spreadsheet_path)
        with self.app.app_context():
            options = {base_constants.CHECK_FOR_WARNINGS: False}
            results = spreadsheet_validate(hed_schema, spreadsheet, options)
            self.assertFalse(results['data'],
                             'spreadsheet_validate results should have empty data when no errors')
            self.assertEqual('success', results['msg_category'],
                             'spreadsheet_validate msg_category should be success when no errors')

    def test_spreadsheet_validate_invalid_excel(self):
        from hedweb.spreadsheet import spreadsheet_validate
        spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelMultipleSheets.xlsx')
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
        hed_schema = hedschema.load_schema(schema_path)
        prefix_dict = {1: "Property/Informational-property/Label/", 3: "Property/Informational-property/Description/"}
        spreadsheet = SpreadsheetInput(spreadsheet_path, worksheet_name='LKT Events',
                                       tag_columns=[4], has_column_names=True,
                                       column_prefix_dictionary=prefix_dict, name=spreadsheet_path)
        with self.app.app_context():
            results = spreadsheet_validate(hed_schema, spreadsheet)
            self.assertTrue(results['data'],
                            'spreadsheet_validate results should have empty data when errors')
            self.assertEqual('warning', results['msg_category'],
                             'spreadsheet_validate msg_category should be warning when no errors')


if __name__ == '__main__':
    unittest.main()
