# sumo_docker_pipeline
- - -

The package `sumo_docker_pipeline` enables you to run a traffic simulator [SUMO](https://sumo.dlr.de/docs/index.html) efficiently 
and to interact with Python easily. 
The package is valid when you need to run SUMO iteratively.

SUMO is often tricky to install locally because of its dependencies. 
Thus, it's a straightforward idea to run SUMO in a docker container.

However, another issue arises when we run SUMO in a docker container. 
It is challenging to construct a pipeline between SUMO and API.

The package provides an easy-to-use API; 
at the same time, 
SUMO runs in a docker container.

# Requirement

- python > 3.5
- docker 
- docker-compose

# Install

## build of a docker image with SUMO

```shell
docker-compose build 
```

## Install a python package

```shell
make install
```

# For developer

```shell
pytest tests
```

# license and credit

The source code is licensed MIT. The website content is licensed CC BY 4.0.



```
@misc{sumo-docker-pipeline,
  author = {Kensuke Mitsuzawa},
  title = {sumo-docker-pipeline},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Kensuke-Mitsuzawa/sumo_docker_pipeline}},
}
```