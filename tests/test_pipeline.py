from sumo_tasks_pipeline.pipeline import DockerPipeline, LocalSumoPipeline
from sumo_tasks_pipeline.file_handler import LocalFileHandler, GcsFileHandler
from pathlib import Path
from sumo_tasks_pipeline.commons.sumo_config_obj import SumoConfigObject
from sumo_tasks_pipeline.commons.result_module import SumoResultObjects
from sumo_tasks_pipeline.static import PATH_PACKAGE_WORK_DIR
import shutil
import uuid


def test_local_pipeline(resource_path_root: Path):
    file_handler = LocalFileHandler(path_save_root=Path(PATH_PACKAGE_WORK_DIR))
    pipeline = LocalSumoPipeline(sumo_command='/usr/local/bin/sumo',
                                 n_jobs=4,
                                 file_handler=file_handler)
    p_copy = f'/tmp/sumo_docker_pipeline_{uuid.uuid1()}'
    shutil.copytree(resource_path_root.joinpath('config_complete'), p_copy)
    sumo_configs = [SumoConfigObject(scenario_name='test',
                                     path_config_dir=resource_path_root.joinpath('config_complete'),
                                     config_name='grid.sumo.cfg'),
                    SumoConfigObject(scenario_name='test2',
                                     path_config_dir=Path(p_copy),
                                     config_name='grid.sumo.cfg')]
    res = pipeline.run_simulation(sumo_configs)
    for r in res:
        assert isinstance(r, SumoResultObjects)


def test_docker_pipeline(resource_path_root: Path):
    file_handler = LocalFileHandler(path_save_root=Path(PATH_PACKAGE_WORK_DIR))
    p_copy = f'/tmp/sumo_docker_pipeline_{uuid.uuid1()}'
    shutil.copytree(resource_path_root.joinpath('config_complete'), p_copy)
    pipeline_obj = DockerPipeline(n_jobs=4, file_handler=file_handler)
    sumo_configs = [SumoConfigObject(scenario_name='test',
                                     path_config_dir=resource_path_root.joinpath('config_complete'),
                                     config_name='grid.sumo.cfg'),
                    SumoConfigObject(scenario_name='test2',
                                     path_config_dir=Path(p_copy),
                                     config_name='grid.sumo.cfg')]
    res = pipeline_obj.run_simulation(sumo_configs=sumo_configs)
    for r in res:
        assert isinstance(r, SumoResultObjects)


if __name__ == '__main__':
    test_local_pipeline(Path('../resources'))
    test_docker_pipeline(Path('../resources'))
