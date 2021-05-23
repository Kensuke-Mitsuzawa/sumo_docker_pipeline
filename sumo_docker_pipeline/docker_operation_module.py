import docker
import lxml.etree
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from sumo_docker_pipeline.result_module import SumoResultObjects, ResultFile
from sumo_docker_pipeline.logger_unit import logger


class SumoDockerController(object):
    def __init__(self,
                 image_name: str = "sumo-docker-pipeline_sumo-docker",
                 container_name_base: str = "sumo-docker",
                 mount_dir_host: str = "mount_dir",
                 mount_dir_container: str = "/mount_dir",
                 sumo_command: str = "sumo",
                 device_rerouting_threads: int = 4):
        self.image_name = image_name
        self.container_name_base = container_name_base
        self.mount_dir_container = mount_dir_container
        self.mount_dir_host = mount_dir_host
        self.sumo_command = sumo_command
        self.device_rerouting_threads = device_rerouting_threads

        self.client = docker.from_env()
        self.__check_connection()

    def __generate_tmp_container_name(self) -> str:
        c_name = f'{self.container_name_base}-{datetime.now().timestamp()}'
        return c_name

    def __check_connection(self):
        c_name = self.__generate_tmp_container_name()
        command_message = self.client.containers.run(image=self.image_name,
                                                     command=self.sumo_command, name=c_name, auto_remove=True)
        assert "German Aerospace Center" in command_message.decode('utf-8')

    def get_sumo_version(self) -> str:
        command_message = self.client.containers.run(image=self.image_name,
                                                     command=f'{self.sumo_command} -V',
                                                     name=self.__generate_tmp_container_name(),
                                                     auto_remove=True)
        return command_message.decode('utf-8')

    @staticmethod
    def extract_output_options(config_file_name: Path) -> Dict[str, ResultFile]:
        """List up files in output directory.

        :param config_file_name:
        :return:
        """
        tree = lxml.etree.parse(config_file_name.open())
        root = tree.getroot()
        r_files_type = []
        for t in root.find('output'):
            element_name = t.tag
            value_name: Dict[str, Any] = t.attrib
            if isinstance(value_name['value'], bool):
                continue
            if value_name['value'] in ('true', 'false'):
                continue
            # end if
            try:
                float(value_name['value'])
                continue
            except ValueError:
                if 'prefix' in element_name:
                    output_dir_name = config_file_name.parent.joinpath(''.join(value_name['value'].split('/')[:-1]))
                else:
                    output_dir_name = config_file_name.parent.joinpath((value_name['value']))
                # end if
                for p_obj in output_dir_name.glob('*'):
                    if p_obj.is_dir():
                        continue
                    # enf if
                    r_files_type.append(ResultFile(p_obj))
                # end for
            # end try
        # end for
        return {f.name_file: f for f in r_files_type}

    def check_output_dir(self, target_scenario_name: str, result_file_types: Dict[str, ResultFile]):
        for tag_name, file_type_obj in result_file_types.items():
            dir_name = file_type_obj.path_file
            # end if
            confirm_target = Path(self.mount_dir_host).joinpath(target_scenario_name).joinpath(dir_name)
            if confirm_target.exists() is False:
                logger.info(f'created a directory {confirm_target}')
                confirm_target.mkdir()
            # end if
        # end for

    @staticmethod
    def __extract_output_dir(path_config_file: Path) -> Path:
        with open(path_config_file, 'r') as f:
            tree = lxml.etree.parse(f)
        # end with
        root = tree.getroot()
        output_prefix_element = root.find('output').find('output-prefix')
        assert output_prefix_element is not None, \
            'output-prefix element does not exist in config file. Check your config file.'
        return Path(path_config_file).parent.joinpath(output_prefix_element.attrib['value'])

    def start_job(self, target_scenario_name: str, config_file_name: str = 'sumo.cfg') -> SumoResultObjects:
        c_name = self.__generate_tmp_container_name()
        path_config_file = Path(self.mount_dir_container).joinpath(target_scenario_name).joinpath(config_file_name)
        job_command = f'{self.sumo_command} -c {path_config_file}'
        if self.device_rerouting_threads > 0:
            job_command += f' --device.rerouting.threads {self.device_rerouting_threads}'
        # end if
        logger.debug(f'executing job with command {job_command}')

        path_config_file_host = Path(self.mount_dir_host).joinpath(target_scenario_name).joinpath(config_file_name)
        command_message = self.client.containers.run(image=self.image_name,
                                                     command=job_command, name=c_name, auto_remove=False,
                                                     volumes={self.mount_dir_host: {'bind': self.mount_dir_container,
                                                                                    'mode': 'rw'}})
        result_file_types = self.extract_output_options(path_config_file_host)
        self.check_output_dir(target_scenario_name, result_file_types)
        res_obj = SumoResultObjects(
            log_message=command_message.decode('utf-8'),
            result_files=result_file_types,
            path_output_dir=self.__extract_output_dir(path_config_file_host)
        )
        return res_obj

    # ---
    # methods for async methods

    def async_start_job(self):
        raise NotImplementedError()

    def async_check_job_status(self):
        raise NotImplementedError()

    def async_get_job_log(self):
        raise NotImplementedError()
