### Run full docker setup
- ```docker-compose up``` Builds and starts the documentation docker image, and a nginx webserver image that are sharing data
- `docker-compose build` Rebuilds (if required) the docker images


### Build and run documentation docker image
- ```docker build -t openframeworks/docs:latest .```
- ```docker run -v $(pwd):/ofDocumentationGenerator -it openframeworks/docs /bin/bash```

### Run Clang parser in docker image
```python /ofDocumentationGenerator/src/documentation_update.py /openframeworks/```

### Run site genererator in docker image
```python /ofDocumentationGenerator/src/generate_site.py``` Outputs in `./_site`
