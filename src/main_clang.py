import clang_parser.clang_parser
import os

of_root = os.path.abspath(os.getenv('OF_ROOT', ''))
json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))

clang_parser.clang_parser.run(of_root, json_data_root)
