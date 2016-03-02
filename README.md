# openFrameworks documentation generator
This is the system that produces and hosts the openFrameworks documentation. It contains several parts:

- **Source code parser** - Based on Python Clang bindings, parses the entire source code of openFrameworks for doxygen style comments and structure.
It outputs the information in a custom JSON structure used internally
- **Markdown parser** - Injects comments from markdown folder into the JSON structure
- **Site generator** - Based on the JSON files, a static HTML site is produced based on the templates in `src/site_generator/templates`
- **Web server** - A nginx instance is used to serve the outputted files
- **Jenkins** - A Jenkins instance that takes webhooks from github, and ssh into the builder and runs the scripts. This is only required on the production machine.

All of these components are bundled in Docker containers so they are very easy to start on your own system

## Run full docker setup
This is what is running on the rackspace server.

- `docker-compose up -d` Builds and starts the documentation docker image, and a nginx webserver image that are sharing data
- `docker-compose build` Rebuilds (if required) the docker images

Jenkins is now running on port `:8080`, and the webserver on `:80`.

## Development Setup
A stripped down version of the docker setup without Jenkins can be run with the following command
```
export OF_PATH=/path/to/local/openFrameworks
export OF_MARKDOWN_DOCUMENTATION_PATH=/path/to/markdown
docker-compose -f docker-compose-devel.yml up -d
```

This will start the builder container and a simple web server on port `:8080`. It mounts the following folders:
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
docker exec ofdocbuilder python /src/main_clang.py
docker exec ofdocbuilder python /src/main_markdown.py
docker exec ofdocbuilder python /src/main_site_generator.py
```

It's also possible to generate only one (or multiple) page by passing the filename to the site generator.
This is useful when working with styling since its much faster
```
docker exec ofdocbuilder python /src/main_site_generator.py ofRectange
```

After this, the site is visible on [192.168.99.100:8080/latest](http://192.168.99.100:8080/latest). Docker ip may vary,
you can find your machine ip by runnning
```
docker-machine ip default
```

## Rackspace Setup
On rackspace following has been done:
- `apt-get update`
- `sudo apt-get install linux-image-extra-$(uname -r)`
- `apt-get install docker docker-compose`
