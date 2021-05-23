from sumo_docker_pipeline.pipeline import DockerPipeline
from pathlib import Path
from sumo_docker_pipeline.logger_unit import logger


def test_pipeline(resource_path_root: Path):
    path_sumo_cfg = resource_path_root.joinpath('config_template/grid.sumo.cfg').absolute()
    path_mounted = resource_path_root.joinpath('config_template').absolute()
    pipeline_obj = DockerPipeline(
        path_config_file=path_sumo_cfg,
        scenario_name='test-scenario')
    values_target = {
        'grid.flows.xml': {
            '/routes/flows/vType[1]': {
                'maxSpeed': 15,
                'minGap': 1.0,
                'accel': 10,
                'decel': 5
            },
            '/routes/flows/vType[2]': {
                'maxSpeed': 10,
                'minGap': 0.5,
                'accel': 5,
                'decel': 5
            }
        }
    }
    result_obj = pipeline_obj.run_simulation(values_target)
    logger.info(result_obj.log_message)
    result_matrix = result_obj.result_files['grid_loop.out.xml'].to_array_objects('flow')
    logger.info(f'result matrix. The mean is {result_matrix.matrix.mean()}')
    import shutil
    shutil.rmtree(pipeline_obj.path_destination_scenario)


if __name__ == '__main__':
    test_pipeline(Path('./resources'))
