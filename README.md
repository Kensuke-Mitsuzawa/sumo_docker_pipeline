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

## Pull the image (or build of a docker image with SUMO)

The existing image is on the [Dockerhub](https://hub.docker.com/repository/docker/kensukemi/sumo-ubuntu18).

```shell
docker pull kensukemi/sumo-ubuntu18
```

If you prefer to build with yourself, you run the following command.

```shell
docker-compose build 
```

## Install a python package

```shell
make install
```

# Example case: iterative run with parameter updates

Let's say that you want to run SUMO iteratively.
At the same time, you want to change input parameters depending on the results of a simulation. 

In that case, you need to check the output of SUMO and update the parameters.
`sumo_docker_pipeline` package enables you to make the process automatic.

[![](https://user-images.githubusercontent.com/1772712/119264146-34563500-bbe2-11eb-9288-2e4e841ff803.png)]()

## Setups

1. creation of a directory where you save SUMO's configuration.
2. creation of template-files of SUMO's configuration.
3. running the pipeline.

## 1. creation of a directory

It is a directory that SUMO accesses.
Let's say that we create `test/resources/config_template`

## 2. creation of SUMO's configuration

You prepare configuration files which SUMO requires.
The format of the conf. files are totally same as SUMO's requirements.

The only difference is that you write wildcard `?` at the place where you wanna replace during pipeline.

For example, `tests/resources/config_template/grid.flows.xml` has the following element,

```xml
<vType vClass="passenger" id="passenger"  tau="0.5" speedDev="0.1" maxSpeed="?" minGap="?" accel="?" decel="?" latAlignment="center" />
```

With the `sumo_docker_pipeline` package, you can replace the attributes with the wildcards `?`.

## 3. running the pipeline

See `examples` directory.



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