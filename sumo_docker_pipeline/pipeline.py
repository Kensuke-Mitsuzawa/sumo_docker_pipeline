from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.config_generation_module import Template2SuMoConfig
from sumo_docker_pipeline.docker_operation_module import SumoDockerController
from sumo_docker_pipeline.result_module import SumoResultObjects


class DockerPipeline(object):
    def __init__(self, mount_dir_path: Path, path_config_file: Path, scenario_name: str):
        time_stamp_current = datetime.now().timestamp()
        self.sumo_controller = SumoDockerController(
            mount_dir_host=str(mount_dir_path),
            container_name_base=f'sumo-docker-{scenario_name}-{time_stamp_current}')
        if not str(Path(mount_dir_path).parent) in str(Path(path_config_file).parent):
            raise Exception('Sumo config file must be under the mounted directory.'
                            f'Sumo-config={path_config_file} '
                            f'Mounted-dir={mount_dir_path}')
        # end if
        path_destination_scenario = Path(mount_dir_path).joinpath(scenario_name)
        if not path_destination_scenario.exists():
            path_destination_scenario.mkdir()
        # end if
        self.path_destination_scenario = path_destination_scenario
        logger.info(f'making a directory at {path_destination_scenario}')
        self.template_generator = Template2SuMoConfig(path_config_file=str(path_config_file),
                                                      path_destination_dir=str(path_destination_scenario))
        self.scenario_name = scenario_name

    def run_simulation(self, value_template: Dict[str, Dict[str, Any]]) -> SumoResultObjects:
        """

        :param value_template:
        :return:
        """
        logger.info(f'making the new config files')
        for c in self.template_generator.get_config_objects():
            if c.name_config_file in value_template:
                c.update_values(value_template[c.name_config_file])
            # end if
        # end for
        self.template_generator.generate_updated_config_file()
        logger.info(f'running sumo simulator now...')
        sumo_result_obj = self.sumo_controller.start_job(target_scenario_name=self.scenario_name,
                                                         config_file_name=self.template_generator.name_sumo_cfg)
        logger.info(f'done the simulation.')
        return sumo_result_obj
