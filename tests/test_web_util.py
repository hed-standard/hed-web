import os
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request, Response
from hedweb.constants import base_constants as bc
from hedweb.constants import file_constants
from tests.test_web_base import TestWebBase


class Test(TestWebBase):

    def test_convert_hed_versions(self):
        from hedweb.web_util import convert_hed_versions
        no_none = {'score': ['1.0.0', '2.0.0']}
        no_none_list = convert_hed_versions(no_none)
        self.assertTrue(no_none_list == ['score_1.0.0', 'score_2.0.0'])
        just_none = {None: ['8.0.0', '8.1.0']}
        just_none_list = convert_hed_versions(just_none)
        self.assertTrue(just_none_list == ['8.0.0', '8.1.0'])
        just_blank = {'': ['9.0.0', '9.1.0']}
        just_blank_list = convert_hed_versions(just_blank)
        self.assertTrue(just_blank_list == ['_9.0.0', '_9.1.0'])
        test_all = {'score': ['1.0.0', '2.0.0'], None: ['8.0.0', '8.1.0']}
        test_all_list = convert_hed_versions(test_all)
        self.assertTrue(test_all_list == ['8.0.0', '8.1.0', 'score_1.0.0', 'score_2.0.0'])

    def test_form_has_file(self):
        from hedweb.web_util import form_has_file
        with self.app.test as _:
            sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
            with open(sidecar_path, 'rb') as fp:
                environ = create_environ(data={'sidecar_file': fp})

            request = Request(environ)
            self.assertTrue(form_has_file(request.files, 'sidecar_file'),
                            "Form has file when no extension requirements")
            self.assertFalse(form_has_file(request.files, 'temp'), "Form does not have file when form name is wrong")
            self.assertFalse(form_has_file(request.files, 'sidecar_file', file_constants.SPREADSHEET_EXTENSIONS),
                             "Form does not have file when extension is wrong")
            self.assertTrue(form_has_file(request.files, 'sidecar_file', [".json"]),
                            "Form has file when extensions and form field match")

    def test_form_has_option(self):
        from hedweb.web_util import form_has_option

        with self.app.test as _:
            environ = create_environ(data={bc.CHECK_FOR_WARNINGS: 'on'})
            request = Request(environ)
            self.assertTrue(form_has_option(request.form, bc.CHECK_FOR_WARNINGS, 'on'),
                            "Form has the required option when set")
            self.assertFalse(form_has_option(request.form, bc.CHECK_FOR_WARNINGS, 'off'),
                             "Form does not have required option when target value is wrong one")
            self.assertFalse(form_has_option(request.form, 'blank', 'on'),
                             "Form does not have required option when option is not in the form")

    def test_form_has_url(self):
        from hedweb.web_util import form_has_url
        with self.app.test as _:
            environ = create_environ(data={bc.SCHEMA_URL: 'https://www.google.com/my.json'})
            request = Request(environ)
            self.assertTrue(form_has_url(request.form, bc.SCHEMA_URL), "Form has a URL that is specified")
            self.assertFalse(form_has_url(request.form, 'temp'), "Form does not have a field that is not specified")
            self.assertFalse(form_has_url(request.form, bc.SCHEMA_URL, file_constants.SPREADSHEET_EXTENSIONS),
                             "Form does not URL with the wrong extension")

    def test_generate_download_file_from_text(self):
        from hedweb.web_util import generate_download_file_from_text
        with self.app.test_request_context():
            the_text = 'The quick brown fox\nIs too slow'
            response = generate_download_file_from_text({'data': the_text, 'msg_category': 'success',
                                                         'msg': 'Successful'})
            self.assertIsInstance(response, Response,
                                  'Generate_response_download_file_from_text returns a response for string')
            self.assertEqual(200, response.status_code,
                             "Generate_response_download_file_from_text has status code 200 for string")
            header_content = dict(response.headers)
            self.assertEqual('success', header_content['Category'], "The msg_category is success")
            self.assertEqual('attachment filename=download.txt', header_content['Content-Disposition'],
                             "generate_download_file has the correct attachment file name")

    def test_generate_download_spreadsheet_excel(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput
            from hedweb.web_util import generate_download_spreadsheet
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelOneSheet.xlsx')

            spreadsheet = SpreadsheetInput(file=spreadsheet_path, file_type='.xlsx',
                                           tag_columns=[4], has_column_names=True,
                                           column_prefix_dictionary={1: 'Attribute/Informational/Label/',
                                                                     3: 'Attribute/Informational/Description/'},
                                           name='ExcelOneSheet.xlsx')
            results = {bc.SPREADSHEET: spreadsheet,
                       bc.OUTPUT_DISPLAY_NAME: 'ExcelOneSheetA.xlsx',
                       bc.MSG: 'Successful download', bc.MSG_CATEGORY: 'success'}
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(response, Response, 'generate_download_spreadsheet returns a response for xlsx files')
            headers_dict = dict(response.headers)
            self.assertEqual(200, response.status_code, 'generate_download_spreadsheet should return status code 200')
            self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response.mimetype,
                             "generate_download_spreadsheet should return spreadsheetml for excel files")
            self.assertTrue(headers_dict['Content-Disposition'].startswith('attachment; filename='),
                            "generate_download_spreadsheet excel should be downloaded as an attachment")

    def test_generate_download_spreadsheet_excel_code(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput
            from hedweb.web_util import generate_download_spreadsheet
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/ExcelOneSheet.xlsx')

            spreadsheet = SpreadsheetInput(file=spreadsheet_path, file_type='.xlsx',
                                           tag_columns=[4], has_column_names=True,
                                           column_prefix_dictionary={1: 'Label/',
                                                                     3: 'Description/'},
                                           name='ExcelOneSheet.xlsx')
            results = {bc.SPREADSHEET: spreadsheet,
                       bc.OUTPUT_DISPLAY_NAME: 'ExcelOneSheetA.xlsx',
                       bc.MSG: 'Successful download', bc.MSG_CATEGORY: 'success'}
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(response, Response, 'generate_download_spreadsheet returns a response for tsv files')
            headers_dict = dict(response.headers)
            self.assertEqual(200, response.status_code, 'generate_download_spreadsheet should return status code 200')
            self.assertEqual('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', response.mimetype,
                             "generate_download_spreadsheet should return spreadsheetml for excel files")
            self.assertTrue(headers_dict['Content-Disposition'].startswith('attachment; filename='),
                            "generate_download_spreadsheet excel should be downloaded as an attachment")

    def test_generate_download_spreadsheet_tsv(self):
        with self.app.test_request_context():
            from hed.models import SpreadsheetInput
            from hedweb.web_util import generate_download_spreadsheet
            spreadsheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            'data/LKTEventCodesHED3.tsv')

            spreadsheet = SpreadsheetInput(file=spreadsheet_path, file_type='.tsv',
                                           tag_columns=[5], has_column_names=True,
                                           column_prefix_dictionary={2: 'Attribute/Informational/Label/',
                                                                     4: 'Attribute/Informational/Description/'},
                                           name='LKTEventCodesHED3.tsv')
            results = {bc.SPREADSHEET: spreadsheet,
                       bc.OUTPUT_DISPLAY_NAME: 'LKTEventCodesHED3.tsv',
                       bc.MSG: 'Successful download', bc.MSG_CATEGORY: 'success'}
            response = generate_download_spreadsheet(results)
            self.assertIsInstance(response, Response, 'generate_download_spreadsheet returns a response for tsv files')
            headers_dict = dict(response.headers)
            self.assertEqual(200, response.status_code, 'generate_download_spreadsheet should return status code 200')
            self.assertEqual('text/plain charset=utf-8', response.mimetype,
                             "generate_download_spreadsheet should return text for tsv files")
            self.assertTrue(headers_dict['Content-Disposition'].startswith('attachment filename='),
                            "generate_download_spreadsheet tsv should be downloaded as an attachment")

    def test_generate_file_name(self):
        from hedweb.web_util import generate_filename
        file1 = generate_filename('mybase')
        self.assertEqual(file1, "mybase", "generate_file_name should return the base when other arguments not set")
        file2 = generate_filename('mybase', name_prefix="prefix")
        self.assertEqual(file2, "prefixmybase", "generate_file_name should return correct name when prefix set")
        file3 = generate_filename('mybase', name_prefix="prefix", extension=".json")
        self.assertEqual(file3, "prefixmybase.json", "generate_file_name should return correct name for extension")
        file4 = generate_filename('mybase', name_suffix="suffix")
        self.assertEqual(file4, "mybasesuffix", "generate_file_name should return correct name when suffix set")
        file5 = generate_filename('mybase', name_suffix="suffix", extension=".json")
        self.assertEqual(file5, "mybasesuffix.json", "generate_file_name should return correct name for extension")
        file6 = generate_filename('mybase', name_prefix="prefix", name_suffix="suffix", extension=".json")
        self.assertEqual(file6, "prefixmybasesuffix.json",
                         "generate_file_name should return correct name for all set")
        filename = generate_filename(None, name_prefix=None, name_suffix=None, extension=None)
        self.assertEqual('', filename, "Return empty when all arguments are none")
        filename = generate_filename(None, name_prefix=None, name_suffix=None, extension='.txt')
        self.assertEqual('', filename,
                         "Return empty when base_name, prefix, and suffix are None, but extension is not")
        filename = generate_filename('c:/temp.json', name_prefix=None, name_suffix=None, extension='.txt')
        self.assertEqual('c_temp.txt', filename,
                         "Returns stripped base_name + extension when prefix, and suffix are None")
        filename = generate_filename('temp.json', name_prefix='prefix_', name_suffix='_suffix', extension='.txt')
        self.assertEqual('prefix_temp_suffix.txt', filename,
                         "Return stripped base_name + extension when prefix, and suffix are None")
        filename = generate_filename(None, name_prefix='prefix_', name_suffix='suffix', extension='.txt')
        self.assertEqual('prefix_suffix.txt', filename,
                         "Returns correct string when no base_name")
        filename = generate_filename('event-strategy-v3_task-matchingpennies_events.json',
                                     name_suffix='_blech', extension='.txt')
        self.assertEqual('event-strategy-v3_task-matchingpennies_events_blech.txt', filename,
                         "Returns correct string when base_name with hyphens")
        filename = generate_filename('HED7.2.0.xml', name_suffix='_blech', extension='.txt')
        self.assertEqual('HED7.2.0_blech.txt', filename, "Returns correct string when base_name has periods")

    def test_generate_file_name_with_date(self):
        from hedweb.web_util import generate_filename
        file1 = generate_filename('mybase')
        file1t = generate_filename('mybase', append_datetime=True)
        self.assertGreater(len(file1t), len(file1), "generate_file_name generates a longer file when datetime is used.")
        # TODO convert more of these tests.
        # self.assertEqual(file1, "mybase", "generate_file_name should return the base when other arguments not set")
        # file2 = generate_filename('mybase', name_prefix="prefix")
        # self.assertEqual(file2, "prefixmybase", "generate_file_name should return correct name when prefix set")
        # file3 = generate_filename('mybase', name_prefix="prefix", extension=".json")
        # self.assertEqual(file3, "prefixmybase.json", "generate_file_name should return correct name for extension")
        # file4 = generate_filename('mybase', name_suffix="suffix")
        # self.assertEqual(file4, "mybasesuffix", "generate_file_name should return correct name when suffix set")
        # file5 = generate_filename('mybase', name_suffix="suffix", extension=".json")
        # self.assertEqual(file5, "mybasesuffix.json", "generate_file_name should return correct name for extension")
        # file6 = generate_filename('mybase', name_prefix="prefix", name_suffix="suffix", extension=".json")
        # self.assertEqual(file6, "prefixmybasesuffix.json",
        #                  "generate_file_name should return correct name for all set")
        # filename = generate_filename(None, name_prefix=None, name_suffix=None, extension=None)
        # self.assertEqual('', filename, "Return empty when all arguments are none")
        # filename = generate_filename(None, name_prefix=None, name_suffix=None, extension='.txt')
        # self.assertEqual('', filename,
        #                  "Return empty when base_name, prefix, and suffix are None, but extension is not")
        # filename = generate_filename('c:/temp.json', name_prefix=None, name_suffix=None, extension='.txt')
        # self.assertEqual('c_temp.txt', filename,
        #                  "Returns stripped base_name + extension when prefix, and suffix are None")
        # filename = generate_filename('temp.json', name_prefix='prefix_', name_suffix='_suffix', extension='.txt')
        # self.assertEqual('prefix_temp_suffix.txt', filename,
        #                  "Return stripped base_name + extension when prefix, and suffix are None")
        # filename = generate_filename(None, name_prefix='prefix_', name_suffix='suffix', extension='.txt')
        # self.assertEqual('prefix_suffix.txt', filename,
        #                  "Returns correct string when no base_name")
        # filename = generate_filename('event-strategy-v3_task-matchingpennies_events.json',
        #                              name_suffix='_blech', extension='.txt')
        # self.assertEqual('event-strategy-v3_task-matchingpennies_events_blech.txt', filename,
        #                  "Returns correct string when base_name with hyphens")
        # filename = generate_filename('HED7.2.0.xml', name_suffix='_blech', extension='.txt')
        # self.assertEqual('HED7.2.0_blech.txt', filename, "Returns correct string when base_name has periods")

    def test_generate_text_response(self):
        with self.app.test_request_context():
            from hedweb.web_util import generate_text_response
            results = {'data': 'testme', bc.MSG: 'testing', bc.MSG_CATEGORY: 'success'}
            response = generate_text_response(results)
            self.assertIsInstance(response, Response, 'generate_download_text_response returns a response')
            headers_dict = dict(response.headers)
            self.assertEqual(200, response.status_code, 'generate_download_text_response should return status code 200')
            self.assertEqual('text/plain charset=utf-8', response.mimetype,
                             "generate_download_download_text_response should return text")
            self.assertEqual(results[bc.MSG], headers_dict['Message'],
                             "generate_download_text_response have the correct message in the response")
            self.assertEqual(results['data'], response.data.decode('utf-8'),
                             "generate_download_text_response have the download text as response data")

    def test_get_hed_schema_from_pull_down_empty(self):
        from hed.errors.exceptions import HedFileError

        from hedweb.web_util import get_hed_schema_from_pull_down
        with self.app.test:
            environ = create_environ(data={})
            request = Request(environ)
            try:
                get_hed_schema_from_pull_down(request)
            except HedFileError:
                pass
            except Exception:
                self.fail('get_hed_schema_from_pull_down threw the wrong exception when data was empty')
            else:
                self.fail('get_hed_schema_from_pull_down should throw a HedFileError exception when data was empty')

    def test_get_hed_schema_from_pull_down_version(self):
        from hed.schema import HedSchema
        from hedweb.web_util import get_hed_schema_from_pull_down
        with self.app.test:
            environ = create_environ(data={bc.SCHEMA_VERSION: '8.0.0'})
            request = Request(environ)
            hed_schema = get_hed_schema_from_pull_down(request)
            self.assertIsInstance(hed_schema, HedSchema,
                                  "get_hed_schema_from_pull_down should return a HedSchema object")

    def test_get_hed_schema_from_pull_down_other(self):
        from hed.schema import HedSchema
        from hedweb.web_util import get_hed_schema_from_pull_down
        with self.app.test:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED8.0.0.xml')
            with open(schema_path, 'rb') as fp:
                environ = create_environ(data={bc.SCHEMA_VERSION: bc.OTHER_VERSION_OPTION,
                                               bc.SCHEMA_PATH: fp})
            request = Request(environ)
            hed_schema = get_hed_schema_from_pull_down(request)
            self.assertIsInstance(hed_schema, HedSchema,
                                  "get_hed_schema_from_pull_down should return a HedSchema object")

    def test_handle_error(self):
        from hed.errors.exceptions import HedFileError, HedExceptions
        from hedweb.web_util import handle_error
        ex = HedFileError(HedExceptions.BAD_PARAMETERS, "This had bad parameters", 'my.file')
        output = handle_error(ex)
        self.assertIsInstance(output, str, "handle_error should return a string if return_as_str")
        output1 = handle_error(ex, return_as_str=False)
        self.assertIsInstance(output1, dict, "handle_error should return a dict if not return_as_str")
        self.assertTrue('message' in output1, "handle_error dict should have a message")
        output2 = handle_error(ex, {'mykey': 'blech'}, return_as_str=False)
        self.assertTrue('mykey' in output2, "handle_error dict should include passed dictionary")

    def test_handle_http_error(self):
        from hed.errors.exceptions import HedFileError, HedExceptions
        from hedweb.web_util import handle_http_error
        with self.app.test_request_context():
            ex = HedFileError(HedExceptions.BAD_PARAMETERS, "This had bad parameters", 'my.file')
            response = handle_http_error(ex)
            headers = dict(response.headers)
            self.assertEqual('error', headers["Category"], "handle_http_error should have category error")
            self.assertTrue(headers['Message'].startswith('badParameters'))
            self.assertFalse(response.data, "handle_http_error should have empty data")
            ex = Exception()
            response = handle_http_error(ex)
            headers = dict(response.headers)
            self.assertEqual('error', headers["Category"], "handle_http_error should have category error")
            self.assertTrue(headers['Message'].startswith('Exception'),
                            "handle_http_error error message starts with the error_type")
            self.assertFalse(response.data, "handle_http_error should have empty data")


if __name__ == '__main__':
    unittest.main()
