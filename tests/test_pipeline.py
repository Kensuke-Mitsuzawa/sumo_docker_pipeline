from sumo_docker_pipeline.pipeline import DockerPipeline, LocalSumoPipeline
from pathlib import Path
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
from sumo_docker_pipeline.commons.result_module import SumoResultObjects
import shutil
import uuid


# def test_local_pipeline(resource_path_root: Path):
#     pipeline = LocalSumoPipeline(sumo_command='/home/kensuke-mi/.pyenv/versions/miniconda3-4.7.12/bin/sumo',
#                                  n_jobs=4)
#     p_copy = f'/tmp/sumo_docker_pipeline_{uuid.uuid1()}'
#     shutil.copytree(resource_path_root.joinpath('config_complete'), p_copy)
#     sumo_configs = [SumoConfigObject(scenario_name='test',
#                                      path_config_dir=resource_path_root.joinpath('config_complete'),
#                                      config_name='grid.sumo.cfg'),
#                     SumoConfigObject(scenario_name='test2',
#                                      path_config_dir=Path(p_copy),
#                                      config_name='grid.sumo.cfg')]
#     res = pipeline.run_simulation(sumo_configs)
#     for r in res.values():
#         assert isinstance(r, SumoResultObjects)


def test_docker_pipeline(resource_path_root: Path):
    p_copy = f'/tmp/sumo_docker_pipeline_{uuid.uuid1()}'
    shutil.copytree(resource_path_root.joinpath('config_complete'), p_copy)
    pipeline_obj = DockerPipeline(n_jobs=4)
    sumo_configs = [SumoConfigObject(scenario_name='test',
                                     path_config_dir=resource_path_root.joinpath('config_complete'),
                                     config_name='grid.sumo.cfg'),
                    SumoConfigObject(scenario_name='test2',
                                     path_config_dir=Path(p_copy),
                                     config_name='grid.sumo.cfg')]
    res = pipeline_obj.run_simulation(sumo_configs=sumo_configs)
    for r in res.values():
        assert isinstance(r, SumoResultObjects)


if __name__ == '__main__':
    test_local_pipeline(Path('../resources'))
    test_docker_pipeline(Path('../resources'))
