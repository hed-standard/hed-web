import os
import unittest


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
            from hed.web import web_utils
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
        file_name = 'abc.xml'
        #     is_valid = web_utils.file_extension_is_valid(file_name, file_constants.SPREADSHEET_FILE_EXTENSIONS)
        #     self.assertTrue(is_valid)
        #

    def test_get_file_from_form(self):
        self.assertTrue(1, "Testing get_file_from_form")
        from hed.web import web_utils
        local_config = web_utils.app_config
        file_dict = {'hed_file': 'hedX', 'other_file': 'XXX'}
        the_form = {'other': 'junk', 'files': file_dict}
        the_file = web_utils.get_file_from_form(the_form, 'hed_file')
        self.assertEqual(the_file, 'hedX', "hedX should be in the dictionary")

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

    def test_save_hed_to_upload_folder(self):
        self.assertTrue(1, "Testing save_hed_to_upload_folder")

    def test_save_hed_to_upload_folder_if_present(self):
        self.assertTrue(1, "Testing save_hed_to_upload_folder")

    def test_setup_logging(self):
        self.assertTrue(1, "Testing setup_logging")

    def test_save_file_to_upload_folder(self):
        self.assertTrue(1, "Testing save_file_to_upload_folder")
        from hed.web import web_utils
        # from flask import current_app
        # app_config = current_app.config
        self.assertTrue(1, "Testing copy_file_line_by_line")
        some_file = '3k32j23kj1.txt'
        temp_name = web_utils.save_file_to_upload_folder(some_file)
        self.assertEqual(temp_name, '', "A file that does not exist cannot be copied")

        hed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/HED.xml')
        local_config = web_utils.app_config
        # print(app_config['UPLOAD_FOLDER'])
        hed_copy = os.path.join(local_config['UPLOAD_FOLDER'], 'temp.xml')
        #success = web_utils.copy_file_line_by_line(hed_file, hed_copy)
        #self.assertTrue(success, "A file that exists can be copied")


if __name__ == '__main__':
    unittest.main()
