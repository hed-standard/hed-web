import os
from hed.schema import load_schema, convert_schema_to_format, get_hed_xml_version

if __name__ == '__main__':
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/HED8.0.0-alpha.1.xml')
    # Load schema and save as legacy XML
    hed_schema = load_schema(hed_file_path=schema_path)
    temp_path, issues = convert_schema_to_format(hed_schema, save_as_legacy_xml=True)
    schema_version = get_hed_xml_version(schema_path)
    print(schema_version)
    if issues:
        print('Had issues')
