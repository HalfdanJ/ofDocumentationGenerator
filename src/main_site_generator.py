from site_generator.generate_site import SiteGenerator
import os
import sys

markdown_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_ROOT', ''))
json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))
site_output = os.path.abspath(os.getenv('OF_DOCUMENTATION_SITE_OUTPUT', './_site'))

generator = SiteGenerator()

if len(sys.argv) > 0:
    generator.file_filter = sys.argv

generator.run(markdown_root, json_data_root, os.path.join(site_output,'latest'))
