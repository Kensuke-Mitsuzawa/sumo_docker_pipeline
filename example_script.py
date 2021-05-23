from sumo_docker_pipeline import DockerPipeline
from sumo_docker_pipeline.logger_unit import logger
from pathlib import Path

"""An example to run SUMO in docker interactively."""

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
    mount_dir_path=path_mounted,
    path_config_file=path_sumo_cfg,
    scenario_name='test-scenario')
result_obj = pipeline_obj.run_simulation(values_target)
# Obtain the result from SUMO
logger.info(result_obj.log_message)
result_matrix = result_obj.result_files['grid_loop.out.xml'].to_array_objects('flow')
logger.info(f'result matrix of flow. Mean={result_matrix.matrix.mean()} Var={result_matrix.matrix.var()}')
import shutil
shutil.rmtree(pipeline_obj.path_destination_scenario)
