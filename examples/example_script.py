import sys
import typing

sys.path.append('../')

from sumo_docker_pipeline import DockerPipeline
from sumo_docker_pipeline import Template2SuMoConfig
from sumo_docker_pipeline import SumoConfigObject
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.static import PATH_PACKAGE_WORK_DIR

from pathlib import Path

"""An example to run SUMO in docker interactively."""


def generate_multiple_simulations(path_sumo_cfg: Path,
                                  flow_configs: typing.Dict[str, typing.Dict],
                                  n_simulation: int) -> typing.List[Path]:
    """Generate "n_simulation" configuration files while updating values following `flow_configs`

    Returns:
        list of `Path` where generated configuration files exist.
    """
    # region update configurations
    seq_mount_dirs = []
    for simulation_i in range(0, n_simulation):
        # a path to directory where docker mounts
        path_mounted = Path(PATH_PACKAGE_WORK_DIR).joinpath(str(simulation_i)).absolute()
        config_convertor = Template2SuMoConfig(path_config_file=path_sumo_cfg, path_destination_dir=path_mounted)
        config_convertor.update_configs({'grid.flows.xml': flow_configs})
        config_convertor.generate_updated_config_file()
        seq_mount_dirs.append(path_mounted)
    # end region
    return seq_mount_dirs


def test_example_iterative():
    """Sample script for a case that "You would like to try SUMO with iterations.
    The second iteration parameter depends on the first iteration value.
    Each iteration consists of multiple simulations."
    """
    # region setup of inputs.
    n_simulation = 3  # number of simulations in one iteration
    n_parallel = 3  # number of parallels
    n_iterations = 2
    resource_path_root = Path('../tests/resources')
    # a path to sumo.cfg file.
    path_sumo_cfg = resource_path_root.joinpath('config_template/grid.sumo.cfg').absolute()
    # key-value which fulfils wildcards in template files. In the case below, grid.flows.xml has wildcard elements.
    flow_configs = {
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
    # endregion

    s_config_files = generate_multiple_simulations(path_sumo_cfg, flow_configs, n_simulation)

    for i_iter in range(0, n_iterations):
        sumo_configs = [SumoConfigObject(scenario_name=dir_config.name, path_config_dir=dir_config, config_name='grid.sumo.cfg')
                        for dir_config in s_config_files]
        pipeline_obj = DockerPipeline(n_jobs=n_parallel)
        result_objs = pipeline_obj.run_simulation(sumo_configs=sumo_configs)
        # Obtain the result from SUMO
        # logger.info(f'result matrix of flow. Mean={result_matrix.matrix.mean()} Var={result_matrix.matrix.var()}')
        # new_passenger_max_speed = result_matrix.matrix.mean() / 30
        # new_pickup_max_speed = result_matrix.matrix.mean() / 20
        # values_target_base['grid.flows.xml']['/routes/flows/vType[1]']['maxSpeed'] = new_passenger_max_speed
        # values_target_base['grid.flows.xml']['/routes/flows/vType[2]']['maxSpeed'] = new_pickup_max_speed
        # seq_mount_dirs.append(pipeline_obj.path_destination_scenario)
    # end for
    # import shutil
    # for path_iter in seq_mount_dirs:
    #     shutil.rmtree(path_iter)
    # end for


if __name__ == '__main__':
    test_example_iterative()

