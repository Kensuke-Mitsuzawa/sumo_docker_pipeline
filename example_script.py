from sumo_docker_pipeline import DockerPipeline
from sumo_docker_pipeline.logger_unit import logger
from pathlib import Path
import tempfile

"""An example to run SUMO in docker interactively."""


def test_example_iterative():
    resource_path_root = Path('tests/resources')
    # a path to sumo.cfg file.
    path_sumo_cfg = resource_path_root.joinpath('config_template/grid.sumo.cfg').absolute()
    # a path to directory where docker mounts
    path_mounted = resource_path_root.joinpath('config_template').absolute()
    # key-value which fulfils wildcards in template files. In the case below, grid.flows.xml has wildcard elements.
    values_target_base = {
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
    seq_mount_dirs = []
    # execution of SUMO in a docker container
    mount_working_dir = tempfile.mkdtemp()
    for i_iter in range(0, 5):
        pipeline_obj = DockerPipeline(
            path_config_file=path_sumo_cfg,
            scenario_name=f'test-scenario-{i_iter}',
            path_mount_working_dir=mount_working_dir)
        result_obj = pipeline_obj.run_simulation(values_target_base)
        # Obtain the result from SUMO
        logger.info(result_obj.log_message)
        result_matrix = result_obj.result_files['grid_loop.out.xml'].to_array_objects('flow')
        logger.info(f'result matrix of flow. Mean={result_matrix.matrix.mean()} Var={result_matrix.matrix.var()}')
        new_passenger_max_speed = result_matrix.matrix.mean() / 30
        new_pickup_max_speed = result_matrix.matrix.mean() / 20
        values_target_base['grid.flows.xml']['/routes/flows/vType[1]']['maxSpeed'] = new_passenger_max_speed
        values_target_base['grid.flows.xml']['/routes/flows/vType[2]']['maxSpeed'] = new_pickup_max_speed
        seq_mount_dirs.append(pipeline_obj.path_destination_scenario)
    # end for
    import shutil
    for path_iter in seq_mount_dirs:
        shutil.rmtree(path_iter)
    # end for

def test_example_one_run():
    resource_path_root = Path('tests/resources')
    # a path to sumo.cfg file.
    path_sumo_cfg = resource_path_root.joinpath('config_template/grid.sumo.cfg').absolute()
    # a path to directory where docker mounts
    path_mounted = resource_path_root.joinpath('config_template').absolute()
    # key-value which fulfils wildcards in template files. In the case below, grid.flows.xml has wildcard elements.
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
    # execution of SUMO in a docker container
    pipeline_obj = DockerPipeline(
        path_config_file=path_sumo_cfg,
        scenario_name='test-scenario')
    result_obj = pipeline_obj.run_simulation(values_target)
    # Obtain the result from SUMO
    logger.info(result_obj.log_message)
    result_matrix = result_obj.result_files['grid_loop.out.xml'].to_array_objects('flow')
    logger.info(f'result matrix of flow. Mean={result_matrix.matrix.mean()} Var={result_matrix.matrix.var()}')
    import shutil
    shutil.rmtree(pipeline_obj.path_destination_scenario)


if __name__ == '__main__':
    test_example_one_run()
    test_example_iterative()

