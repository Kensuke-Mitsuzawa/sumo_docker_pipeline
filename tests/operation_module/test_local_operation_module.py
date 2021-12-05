from sumo_docker_pipeline.operation_module.local_operation_module import LocalSumoController
from pathlib import Path


def test_container_init(resource_path_root: Path):
    controller = LocalSumoController(
        sumo_command='/home/kensuke-mi/.pyenv/versions/miniconda3-4.7.12/bin/sumo',
        path_sumo_config=resource_path_root.joinpath('config_complete'))


def test_start_job(resource_path_root: Path):
    controller = LocalSumoController(
        sumo_command='/home/kensuke-mi/.pyenv/versions/miniconda3-4.7.12/bin/sumo',
        path_sumo_config=resource_path_root.joinpath('config_complete'))
    controller.get_sumo_version()
    job_result = controller.start_job(config_file_name='grid.sumo.cfg', target_scenario_name='config_complete')


if __name__ == '__main__':
    p_sumo_resource = Path('../resources').absolute()
    test_container_init(p_sumo_resource)
    test_start_job(p_sumo_resource)

