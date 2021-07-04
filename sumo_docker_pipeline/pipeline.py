from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Dict, Any, Optional
from tempfile import mkdtemp
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.config_generation_module import Template2SuMoConfig
from sumo_docker_pipeline.docker_operation_module import SumoDockerController
from sumo_docker_pipeline.result_module import SumoResultObjects


class DockerPipeline(object):
    def __init__(self,
                 path_config_file: Path,
                 scenario_name: str,
                 path_mount_working_dir: Optional[Path] = None,
                 docker_image_name: str = 'kensukemi/sumo-ubuntu18',
                 is_rewrite_windows_path: bool = True):
        """A pipeline interface to run SUMO-docker.

        :param path_config_file: a path to sumo.cfg file.
        The other config files should be in the same directory (or under the sub-directory)
        :param scenario_name: a name of scenario
        :param path_mount_working_dir: A path to directory where a container mount as the shared directory.
        :param docker_image_name: A name of docker-image that you call.
        :param is_rewrite_windows_path:
        """
        if path_mount_working_dir is None:
            self.path_mount_working_dir = Path(mkdtemp()).absolute()
        else:
            self.path_mount_working_dir = path_mount_working_dir.absolute()
        # end if

        path_destination_scenario = Path(self.path_mount_working_dir).joinpath(scenario_name)
        if not path_destination_scenario.exists():
            path_destination_scenario.mkdir()
        # end if
        self.path_destination_scenario = path_destination_scenario
        logger.info(f'making a directory at {path_destination_scenario}')
        self.template_generator = Template2SuMoConfig(path_config_file=str(path_config_file),
                                                      path_destination_dir=str(path_destination_scenario))
        self.scenario_name = scenario_name
        self.docker_image_name = docker_image_name
        self.is_rewrite_windows_path = is_rewrite_windows_path

    def get_data_directory(self) -> Path:
        return self.path_mount_working_dir

    def run_simulation(self,
                       value_template: Dict[str, Dict[str, Any]],
                       device_rerouting_threads: int = 4,
                       is_overwrite: bool = False) -> SumoResultObjects:
        """Run SUMO simulation in a docker container.

        :param value_template: A multi layer dict object which replaces values in template files.
        Put blank dict {} if there is no parameter to be replaced.
        :param device_rerouting_threads: --device.rerouting.threads option of SUMO.
        The option makes simulations in multi-thread.
        :param is_overwrite: True, then the method overwrites outputs from SUMO.
        False raises Exception if there is a destination directory already. Default False.
        :return:
        """
        logger.info(f'making the new config files')
        for c in self.template_generator.get_config_objects():
            if c.name_config_file in value_template:
                c.update_values(value_template[c.name_config_file])
            # end if
        # end for
        if self.path_destination_scenario.exists() and is_overwrite is False:
            raise Exception(f'{str(self.path_mount_working_dir)} exists already. '
                            f'Put is_overwrite=True if you want to save the result in the same directory.')
        # end if
        self.template_generator.generate_updated_config_file()
        logger.info(f'running sumo simulator now...')
        time_stamp_current = datetime.now().timestamp()
        sumo_controller = SumoDockerController(
            mount_dir_host=str(self.path_mount_working_dir),
            container_name_base=f'sumo-docker-{self.scenario_name}-{time_stamp_current}',
            device_rerouting_threads=device_rerouting_threads,
            image_name=self.docker_image_name)
        sumo_result_obj = sumo_controller.start_job(target_scenario_name=self.scenario_name,
                                                    config_file_name=self.template_generator.name_sumo_cfg)
        logger.info(f'done the simulation.')
        return sumo_result_obj
