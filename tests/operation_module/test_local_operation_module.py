from sumo_docker_pipeline.operation_module.local_operation_module import LocalSumoController
from pathlib import Path
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject

PATH_SUMO = '/usr/local/bin/sumo'


def test_container_init(resource_path_root: Path):
    controller = LocalSumoController(sumo_command=PATH_SUMO)


def test_start_job(resource_path_root: Path):
    controller = LocalSumoController(sumo_command=PATH_SUMO,
                                     is_compress_result=True)
    controller.get_sumo_version()
    obj = SumoConfigObject(scenario_name='test',
                     path_config_dir=resource_path_root.joinpath('config_complete'),
                     config_name='grid.sumo.cfg')
    job_result = controller.start_job(obj)
    assert job_result.path_output_dir.exists()


if __name__ == '__main__':
    p_sumo_resource = Path('../resources').absolute()
    test_container_init(p_sumo_resource)
    test_start_job(p_sumo_resource)

