from sumo_docker_pipeline.operation_module.docker_operation_module import SumoDockerController
from pathlib import Path
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject


def test_container_init():
    controller = SumoDockerController()


def test_start_job(resource_path_root: Path):
    controller = SumoDockerController(mount_dir_host=resource_path_root)
    obj = SumoConfigObject(scenario_name='test',
                     path_config_dir=resource_path_root.joinpath('config_complete'),
                     config_name='grid.sumo.cfg')
    job_result = controller.start_job(obj)


if __name__ == '__main__':
    test_container_init()
    test_start_job(Path('resources').absolute())
