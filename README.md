# sumo-tasks-pipeline
- - -

Run SUMO simulators as easy as possible!

The package `sumo-tasks-pipeline` enables you to run a traffic simulator [SUMO](https://sumo.dlr.de/docs/index.html) efficiently 
and to interact with Python easily.

# Example

Just three lines to run a SUMO simulation.

```python
from sumo_tasks_pipeline import LocalSumoController, SumoConfigObject
from pathlib import Path

path_config = Path().cwd().joinpath('tests/resources/config_complete')
sumo_controller = LocalSumoController(sumo_command='/usr/local/bin/sumo')
sumo_config = SumoConfigObject(scenario_name='example', path_config_dir=path_config, config_name='grid.sumo.cfg')
sumo_result_obj = sumo_controller.start_job(sumo_config)
```

See `examples` directory to know more.

# Features

- Possible to resume your tasks. The feature is useful when you run simulators on Google Colab.
- Possible to save SUMO simulation result to Google Cloud Storage (GCS). No worries even when your local storage is small.
- Possible to run SUMO simulations with multiple machines if you use GCS as the storage backend.

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


# For developer

```shell
pytest tests
```

# license and credit

The source code is licensed MIT. The website content is licensed CC BY 4.0.


```
@misc{sumo-docker-pipeline,
  author = {Kensuke Mitsuzawa},
  title = {sumo-tasks-pipeline},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/Kensuke-Mitsuzawa/sumo_docker_pipeline}},
}
```