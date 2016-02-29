from site_generator.generate_site import SiteGenerator
import os


markdown_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_ROOT', ''))
json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))
site_output = os.path.abspath(os.getenv('OF_DOCUMENTATION_SITE_OUTPUT', './_site'))

generator = SiteGenerator()
generator.run(markdown_root, json_data_root, os.path.join(site_output,'latest'))
