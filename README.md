### Run full docker setup
- Set openframeworks path `export OF_PATH=/path/to/openframeworks/`
- ```docker-compose up``` Builds and starts the documentation docker image, and a nginx webserver image that are sharing data
- `docker-compose build` Rebuilds (if required) the docker images


### Build image manually and run documentation docker image
- ```docker build -t openframeworks/docs:latest .```
- ```docker run -v $(pwd):/ofDocumentationGenerator -v $(OF_PATH):/openframeworks -it openframeworks/docs /bin/bash```

### Run Clang parser in docker image
```python /ofDocumentationGenerator/src/main.py /openframeworks/```

### Run site genererator in docker image
```python /ofDocumentationGenerator/src/generate_site.py``` Outputs in `./_site`

## Rackspace setup
On rackspace following has been done:
- `apt-get update`
- `sudo apt-get install linux-image-extra-$(uname -r)`
- `apt-get install docker docker-compose`
