import markdown_parser.parse_markdown
import os

json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))
markdown_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_ROOT', ''))

markdown_parser.parse_markdown.run(markdown_root, json_data_root)
