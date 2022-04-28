from sumo_tasks_pipeline.commons.result_module import SumoResultObjects
from sumo_tasks_pipeline.commons.result_module import ResultFile
from sumo_tasks_pipeline.commons.sumo_config_obj import SumoConfigObject
from pathlib import Path


def test_generate_output(resource_path_root: Path):
    path_output_dir = resource_path_root.joinpath('config_complete/output')
    obj = SumoConfigObject(scenario_name='test',
                           path_config_dir=resource_path_root.joinpath('config_complete'),
                           config_name='grid.sumo.cfg')
    result_generator = SumoResultObjects(
        id_scenario='test',
        sumo_config_obj=obj,
        log_message='',
        path_output_dir=path_output_dir)


if __name__ == '__main__':
    test_generate_output(Path('./resources'))
