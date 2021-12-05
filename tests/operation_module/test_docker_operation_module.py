from sumo_docker_pipeline.operation_module.docker_operation_module import SumoDockerController
from pathlib import Path


def test_container_init():
    controller = SumoDockerController()


def test_start_job(resource_path_root: Path):
    controller = SumoDockerController(mount_dir_host=resource_path_root)
    job_result = controller.start_job(config_file_name='grid.sumo.cfg', target_scenario_name='config_complete')


if __name__ == '__main__':
    test_container_init()
    test_start_job(Path('resources').absolute())
