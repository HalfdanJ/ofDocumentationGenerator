## openFrameworks documentation generator
This is the system that produces and hosts the openFrameworks documentation. It contains several parts:

- **Source code parser** - Based on Python Clang bindings, parses the entire source code of openFrameworks for doxygen style comments and structure.
It outputs the information in a custom JSON structure used internally
- **Markdown parser** - Injects comments from markdown folder into the JSON structure
- **Site generator** - Based on the JSON files, a static HTML site is produced based on the templates in `src/templates`

## Run full docker setup
- `docker-compose up -d` Builds and starts the documentation docker image, and a nginx webserver image that are sharing data
- `docker-compose build` Rebuilds (if required) the docker images

## Run development setup
A stripped down version of the docker setup without Jenkins can be run with the following command
```
export OF_PATH=/path/to/local/openFrameworks
export OF_MARKDOWN_DOCUMENTATION_PATH=/path/to/markdown
docker-compose -f docker-compose-devel.yml up -d
```

This will start the builder container and a simple web server on port 8080. It mounts the following folders:
- openFrameworks (read only), based on `OF_PATH`
- markdown (read only), based on `OF_MARKDOWN_DOCUMENTATION_PATH`
- `./src` (read only), the python source code of the builder
- `./_output`, the output directory where the html is produced, and json data

To run the builder, run the following command:
```
docker exec ofdocbuilder python /src/main.py
```

Alternatively you can run parts of the process
```
docker exec ofdocbuilder python /src/clang_parser.py
docker exec ofdocbuilder python /src/parse_markdown.py
docker exec ofdocbuilder python /src/generate_site.py
```

After this, the site is visible on `http://youlocalip:8080/latest`
(it needs to be your local ip, and not localhost)

## Rackspace setup
On rackspace following has been done:
- `apt-get update`
- `sudo apt-get install linux-image-extra-$(uname -r)`
- `apt-get install docker docker-compose`
