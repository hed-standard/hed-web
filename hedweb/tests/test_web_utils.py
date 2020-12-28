import os
import unittest
from unittest.mock import Mock


from hed.web.app_factory import AppFactory
import shutil
# from hed.util import hed_cache
# #from hed.web.utils import app_config, initialize_worksheets_info_dictionary
# from hed.web.constants import file_constants, spreadsheet_constants


# app = AppFactory.create_app('config.TestConfig')
# with app.app_context():
#     from hed.web import web_utils
#     from hed.web.routes import route_blueprint
#
#     app.register_blueprint(route_blueprint, url_prefix=app.config['URL_PREFIX'])
#     web_utils.create_upload_directory(app.config['UPLOAD_FOLDER'])
#     hed_cache.set_cache_directory(app.config['HED_CACHE_FOLDER'])
# with app.app_context():
#     from hed.web import web_utils
#     from hed.web.routes import route_blueprint
#
#     app.register_blueprint(route_blueprint, url_prefix=app.config['URL_PREFIX'])
#     web_utils.create_upload_directory(app.config['UPLOAD_FOLDER'])

class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upload_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/upload')
        app = AppFactory.create_app('config.TestConfig')
        with app.app_context():

            from hed.web.routes import route_blueprint
            app.register_blueprint(route_blueprint)
            if not os.path.exists(cls.upload_directory):
                os.mkdir(cls.upload_directory)
            app.config['UPLOAD_FOLDER'] = cls.upload_directory
            cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.upload_directory)

    def test_check_if_option_in_form(self):
        self.assertTrue(1, "Testing check_if_option_in_form")

    def test_create_upload_directory(self):
        self.assertTrue(1, "Testing create_upload_directory")

    def test_file_has_valid_extension(self):
        self.assertTrue(1, "Testing file_has_valid_extension")

    def test_file_extension_is_valid(self):
        self.assertTrue(1, "Testing file_extension_is_valid")
        from hed.web import web_utils
        is_valid = web_utils.file_extension_is_valid('abc.xml', ['.xml', '.txt'])
        self.assertTrue(is_valid, 'File name has a valid extension if the extension is in list of valid extensions')
        is_valid = web_utils.file_extension_is_valid('abc.XML', ['.xml', '.txt'])
        self.assertTrue(is_valid, 'File name has a valid extension if capitalized version of valid extension')
        is_valid = web_utils.file_extension_is_valid('abc.temp', ['.xml', '.txt'])
        self.assertFalse(is_valid, 'File name has a valid extension if the extension not in list of valid extensions')
        file_name = 'abc'
        is_valid = web_utils.file_extension_is_valid('abc')
        self.assertTrue(is_valid, 'File names with no extension are valid when no valid extensions provided')
        is_valid = web_utils.file_extension_is_valid('abc', ['.xml', '.txt'])
        self.assertFalse(is_valid, 'File name has a valid extension if the extension not in list of valid extensions')
        is_valid = web_utils.file_extension_is_valid('C:abc.Txt', ['.xml', '.txt'])
        self.assertTrue(is_valid, 'File name has a valid extension if the extension is in list of valid extensions')

    def test_get_original_filename(self):
        self.assertTrue(1, "Testing get_original_filename")
        # from hed.web import web_utils
        # local_config = web_utils.app_config
        # request_form = Mock()
        # request_form.files = {'hed_file': 'hedX', 'other_file': 'XXX'}
        #
        #
        # #get_original_filename(form_request_object, file_key, valid_extensions)
        # the_file = web_utils. get_original_filename(request_form, 'hed_file')
        # self.assertEqual(the_file, 'hedX', "hedX should be in the dictionary")

    def test_find_hed_version_in_uploaded_file(self):
        self.assertTrue(1, "Testing find_hed_version_in_uploaded_file")

    def test_find_major_hed_versions(self):
        self.assertTrue(1, "Testing find_major_hed_versions")
        # def test_find_major_hed_versions(self):
        #     #self.create_test_app()
        #     hed_info = utils.find_major_hed_versions()
        #     self.assertTrue(self.major_version_key in hed_info)

    def test_generate_download_file_response(self):
        self.assertTrue(1, "Testing generate_download_file_response")

    def test_get_hed_path_from_form(self):
        self.assertTrue(1, "Testing get_hed_path_from_form")

    def test_handle_http_error(self):
        self.assertTrue(1, "Testing handle_http_error")

    def test_save_file_to_upload_folder(self):
        self.assertTrue(1, "Testing save_file_to_upload_folder")
        #import hed.web.web_utils
        from hed.web.web_utils import save_file_to_upload_folder, app_config
        #from flask import current_app
        local_config = app_config
        self.assertTrue(1, "Testing copy_file_line_by_line")
        some_file = '3k32j23kj1.txt'
        temp_name = save_file_to_upload_folder(some_file)
        self.assertEqual(temp_name, '', "A file that does not exist cannot be copied")

        hed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED.xml')

        # print(app_config['UPLOAD_FOLDER'])
        hed_copy = os.path.join(local_config['UPLOAD_FOLDER'], 'temp.xml')
        #success = web_utils.copy_file_line_by_line(hed_file, hed_copy)
        #self.assertTrue(success, "A file that exists can be copied")

    def test_setup_logging(self):
        self.assertTrue(1, "Testing setup_logging")


if __name__ == '__main__':
    unittest.main()
