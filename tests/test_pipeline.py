from sumo_docker_pipeline.pipeline import DockerPipeline, LocalSumoPipeline
from pathlib import Path
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
import shutil
import uuid

def test_local_pipeline(resource_path_root: Path):
    pipeline = LocalSumoPipeline(sumo_command='/home/kensuke-mi/.pyenv/versions/miniconda3-4.7.12/bin/sumo',
                                 n_jobs=4)
    p_copy = f'/tmp/sumo_docker_pipeline_{uuid.uuid1()}'
    shutil.copytree(resource_path_root.joinpath('config_complete'), p_copy)
    sumo_configs = [SumoConfigObject(scenario_name='test',
                                     path_config=resource_path_root.joinpath('config_complete'),
                                     config_name='grid.sumo.cfg'),
                    SumoConfigObject(scenario_name='test2',
                                     path_config=Path(p_copy),
                                     config_name='grid.sumo.cfg')]
    res = pipeline.run_simulation(sumo_configs)


# def test_pipeline(resource_path_root: Path):
#     path_sumo_cfg = resource_path_root.joinpath('config_template/grid.sumo.cfg').absolute()
#     path_mounted = resource_path_root.joinpath('config_template').absolute()
#     pipeline_obj = DockerPipeline(
#         path_config_file=path_sumo_cfg,
#         scenario_name='test-scenario')
#     values_target = {
#         'grid.flows.xml': {
#             '/routes/flows/vType[1]': {
#                 'maxSpeed': 15,
#                 'minGap': 1.0,
#                 'accel': 10,
#                 'decel': 5
#             },
#             '/routes/flows/vType[2]': {
#                 'maxSpeed': 10,
#                 'minGap': 0.5,
#                 'accel': 5,
#                 'decel': 5
#             }
#         }
#     }
#     result_obj = pipeline_obj.run_simulation(values_target, is_overwrite=True)
#     logger.info(result_obj.log_message)
#     result_matrix = result_obj.result_files['grid_loop.out.xml'].to_array_objects('flow')
#     logger.info(f'result matrix. The mean is {result_matrix.matrix.mean()}')
#     import shutil
#     shutil.rmtree(pipeline_obj.path_destination_scenario)


if __name__ == '__main__':
    test_local_pipeline(Path('../resources'))
