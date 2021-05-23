from sumo_docker_pipeline.docker_operation_module import SumoDockerController
from pathlib import Path


def test_container_init():
    controller = SumoDockerController()


def test_start_job(resource_path_root: Path):
    controller = SumoDockerController(mount_dir_host=str(resource_path_root.absolute()))
    job_result = controller.start_job(target_scenario_name='', config_file_name='grid.sumo.cfg')


if __name__ == '__main__':
    test_container_init()
    test_start_job(Path('./resources'))
