### Run full docker setup
```docker-compose up``` Builds and starts the documentation docker image, and a nginx webserver image that are sharing data

### Build and run documentation docker image
```docker build -t openframeworks/docs:latest .```
```docker run -t openframeworks/docs -v .:/ofDocumentationGenerator /bin/bash```

### Run Clang parser in docker image
```python /ofDocumentationGenerator/generator/documentation_update.py /openframeworks/```

### Run site genererator in docker image
```python /ofDocumentationGenerator/generator/generate_site.py``` Outputs in `./_site`
