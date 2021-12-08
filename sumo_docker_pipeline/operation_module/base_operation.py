import lxml.etree
import re
from typing import Dict, Any
from pathlib import Path
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
from sumo_docker_pipeline.commons.result_module import SumoResultObjects, ResultFile


class BaseController(object):
    def __init__(self,
                 sumo_command: str = "sumo",
                 is_rewrite_windows_path: bool = True):
        self.sumo_command = sumo_command
        self.is_rewrite_windows_path = is_rewrite_windows_path

    def check_connection(self):
        raise NotImplementedError()

    def get_sumo_version(self) -> str:
        raise NotImplementedError()

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

    @staticmethod
    def check_output_dir(path_working_dir: Path,
                         target_scenario_name: str,
                         result_file_types: Dict[str, ResultFile]):
        """Creates directory for SUMO output. SUMO raises up Exception if there were NOT a directory for outputs.

        Args:
            path_working_dir: Path to a working directory.
            target_scenario_name: any scenario-name
            result_file_types: {name-of-output-file: Path to directory for saving}

        Returns: None
        """
        for tag_name, file_type_obj in result_file_types.items():
            dir_name = file_type_obj.path_file
            # end if
            confirm_target = Path(path_working_dir).joinpath(target_scenario_name).joinpath(dir_name)
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
        Ex. C:\\Users\\kensu\\AppData\\Local\\Temp\\tmp3t95r_eb -> /c/Users/kensu/AppData/Local/Temp/tmp3t95r_eb
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

    def start_job(self, path_sumo_config: SumoConfigObject) -> SumoResultObjects:
        raise NotImplementedError()
