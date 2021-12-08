import shutil
import uuid

import docker
import lxml.etree
import re
from typing import Dict, Any
from pathlib import Path, WindowsPath
from datetime import datetime
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.operation_module.base_operation import BaseController
from sumo_docker_pipeline import static
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
from sumo_docker_pipeline.commons.result_module import SumoResultObjects, ResultFile

from docker.errors import NotFound


class SumoDockerController(BaseController):
    def __init__(self,
                 image_name: str = "kensukemi/sumo-ubuntu18",
                 container_name_base: str = "sumo-docker",
                 mount_dir_host: Path = Path(static.PATH_PACKAGE_WORK_DIR).joinpath(static.DIR_NAME_DOCKER_MOUNT),
                 mount_dir_container: str = "/mount_dir",
                 sumo_command: str = "sumo",
                 is_rewrite_windows_path: bool = True,
                 docker_client: docker.DockerClient = None):
        super(SumoDockerController, self).__init__(
            sumo_command=sumo_command,
            is_rewrite_windows_path=is_rewrite_windows_path)
        self.image_name = image_name
        self.container_name_base = container_name_base
        self.mount_dir_container = mount_dir_container
        self.mount_dir_host = mount_dir_host
        self.sumo_command = sumo_command

        self.is_auto_remove = True
        if docker_client is None:
            self.client = docker.from_env()
        else:
            self.client = docker_client
        # end if
        self.check_connection()
        self.is_rewrite_windows_path = is_rewrite_windows_path

    def __generate_tmp_container_name(self) -> str:
        c_name = f'{self.container_name_base}-{datetime.now().timestamp()}'
        return c_name

    def check_connection(self):
        c_name = self.__generate_tmp_container_name()
        try:
            command_message = self.client.containers.run(image=self.image_name,
                                                         command=self.sumo_command, name=c_name,
                                                         auto_remove=self.is_auto_remove)
        except docker.errors.NotFound:
            self.is_auto_remove = False
            command_message = self.client.containers.run(image=self.image_name,
                                                         command=self.sumo_command, name=c_name,
                                                         auto_remove=self.is_auto_remove)
        # end except
        assert "German Aerospace Center" in command_message.decode('utf-8')

    def detect_mount_point(self):
        candidate_mount_points = [str(Path(self.mount_dir_container).parent), '/home', '/tmp']
        for path_candidate in candidate_mount_points:
            container_name = self.__generate_tmp_container_name()
            command_message = \
                self.client.containers.run(image=self.image_name,
                                           command=f'ls {path_candidate}', name=container_name,
                                           auto_remove=self.is_auto_remove,
                                           volumes={
                                               self.mount_dir_host: {'bind': f'{path_candidate}/mount_dir',
                                                                     'mode': 'rw'}})
            if self.is_auto_remove is False:
                self.delete_container(container_name)
            # end if
            if 'mount_dir' in command_message.decode('utf-8'):
                return path_candidate
            # end if
        # end for
        raise Exception(f'Failed to mount host-directory into container-directory. '
                        f'Try to change mount_dir_container argument of init. '
                        f'Current value is {self.mount_dir_container}')

    def delete_container(self, container_name: str):
        for c in self.client.containers.list(all=True):
            if c.name == container_name:
                try:
                    c.remove()
                except Exception as e:
                    logger.warning(f'We failed to remove container = {container_name}. '
                                   f'We recommend to remove it manually. '
                                   f'The reason is {e}')

    def get_sumo_version(self) -> str:
        command_message = self.client.containers.run(image=self.image_name,
                                                     command=f'{self.sumo_command} -V',
                                                     name=self.__generate_tmp_container_name(),
                                                     auto_remove=self.is_auto_remove)
        return command_message.decode('utf-8')

    @staticmethod
    def extract_output_options(config_file_name: Path) -> Dict[str, ResultFile]:
        """List up files in output directory.

        Args:
            config_file_name:
        Returns:
            {"type of config": `ResultFile`}
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
    def extract_output_dir(path_config_file: Path) -> Path:
        with open(path_config_file, 'r') as f:
            tree = lxml.etree.parse(f)
        # end with
        root = tree.getroot()
        output_prefix_element = root.find('output').find('output-prefix')
        assert output_prefix_element is not None, \
            'output-prefix element does not exist in config file. Check your config file.'
        return Path(path_config_file).parent.joinpath(output_prefix_element.attrib['value'])

    @staticmethod
    def rewrite_windows_path(mount_dir_host: str) -> str:
        """rewrite from Windows style into Unix style.
        Ex. C:\\Users\\kensu\\AppData\\Local\\Temp\\tmp3t95r_eb
        -> /c/Users/kensu/AppData/Local/Temp/tmp3t95r_eb
        """
        unix_form = Path(mount_dir_host).as_posix()
        drive_prefix = re.search(r'^[C-D]\:', str(unix_form))
        if drive_prefix:
            without_prefix = unix_form[drive_prefix.span()[1]:]
            replaced_prefix = '/' + unix_form[drive_prefix.span()[0]:drive_prefix.span()[1]].lower().replace(':', '')
            path_updated = replaced_prefix + without_prefix
        else:
            path_updated = str(unix_form)
        # end if
        return path_updated

    def start_job(self, sumo_config: SumoConfigObject) -> SumoResultObjects:
        c_name = self.__generate_tmp_container_name()
        # region copy to tmp directory
        suffix_uuid = str(uuid.uuid4())
        shutil.copytree(sumo_config.path_config_dir, self.mount_dir_host.joinpath(suffix_uuid))
        # endregion

        # region set Path inside container.
        path_config_file_container = Path(self.mount_dir_container).joinpath(suffix_uuid).\
            joinpath(sumo_config.config_name)
        if self.is_rewrite_windows_path and isinstance(path_config_file_container, WindowsPath):
            # If windows...Path structure is broken. Fix it manually.
            path_config_file = path_config_file_container.as_posix()
        else:
            path_config_file = path_config_file_container
        # end if
        job_command = f'{self.sumo_command} -c {path_config_file}'
        # endregion

        if self.is_rewrite_windows_path and isinstance(Path('./'), WindowsPath):
            # from windows style path into Unix style path. Docker does not accept Windows format.
            logger.info('I replaced a format of source directory in the host side. '
                        'Check it if there is an unknown issue.')
            logger.info(f'Before {self.mount_dir_host}')
            mount_dir_host = self.rewrite_windows_path(str(self.mount_dir_host))
            logger.info(f'After {mount_dir_host}')
        else:
            mount_dir_host = str(self.mount_dir_host)
        # end if
        logger.debug(f'executing job with command {job_command}')

        command_message = self.client.containers.run(image=self.image_name,
                                                     command=job_command,
                                                     name=c_name,
                                                     auto_remove=self.is_auto_remove,
                                                     volumes={mount_dir_host: {'bind': self.mount_dir_container,
                                                                               'mode': 'rw'}})
        path_config_file_host = self.mount_dir_host.joinpath(suffix_uuid).\
            joinpath(sumo_config.config_name)
        result_file_types = self.extract_output_options(path_config_file_host)
        res_obj = SumoResultObjects(
            id_scenario=sumo_config.scenario_name,
            sumo_config_obj=sumo_config,
            log_message=command_message.decode('utf-8'),
            result_files=result_file_types,
            path_output_dir=self.extract_output_dir(path_config_file_host)
        )
        if self.is_auto_remove is False:
            self.delete_container(container_name=c_name)
        # end if
        return res_obj
