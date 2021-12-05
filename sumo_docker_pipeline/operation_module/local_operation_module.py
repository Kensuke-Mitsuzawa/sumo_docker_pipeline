from pathlib import Path, WindowsPath
import subprocess
from sumo_docker_pipeline.result_module import SumoResultObjects
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.operation_module.base_operation import BaseController


class LocalSumoController(BaseController):
    def __init__(self,
                 path_sumo_config: Path,
                 sumo_command: str = "/bin/sumo",
                 is_rewrite_windows_path: bool = True):
        super(LocalSumoController, self).__init__(
            sumo_command=sumo_command,
            is_rewrite_windows_path=is_rewrite_windows_path)
        assert path_sumo_config.exists()
        self.path_sumo_config = path_sumo_config
        self.check_connection()

    def check_connection(self):
        sumo_bash_command = [self.sumo_command]
        pipe_obj = subprocess.Popen(sumo_bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = pipe_obj.communicate()
        r_code = pipe_obj.returncode
        assert r_code == 0
        assert "German Aerospace Center" in outs.decode('utf-8')

    def get_sumo_version(self) -> str:
        sumo_bash_command = [self.sumo_command, '-V']
        pipe_obj = subprocess.Popen(sumo_bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = pipe_obj.communicate()
        r_code = pipe_obj.returncode
        assert r_code == 0
        return outs.decode('utf-8')

    def start_job(self, config_file_name: str = 'sumo.cfg', target_scenario_name: str = None) -> SumoResultObjects:
        """Run SUMO on local.

        Args:
            target_scenario_name: Nothing. Keep it None.
            config_file_name: "sumo.cfg" name.

        Returns: `SumoResultObjects`
        """
        path_config_file = Path(self.path_sumo_config).joinpath(config_file_name)
        if self.is_rewrite_windows_path and isinstance(path_config_file, WindowsPath):
            # If windows...Path structure is broken. Fix it manually.
            path_config_file = path_config_file.as_posix()
        # end if
        job_command = f'{self.sumo_command} -c {path_config_file}'
        logger.debug(f'executing job with command {job_command}')

        sumo_bash_command = [self.sumo_command, '-c', path_config_file]
        pipe_obj = subprocess.Popen(sumo_bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = pipe_obj.communicate()
        r_code = pipe_obj.returncode
        assert r_code == 0

        path_config_file_host = Path(self.path_sumo_config).joinpath(config_file_name)
        # todo delete
        # result_file_types = self.extract_output_options(path_config_file_host)
        # self.check_output_dir(target_scenario_name, result_file_types)
        res_obj = SumoResultObjects(
            log_message=outs.decode('utf-8'),
            path_output_dir=self.extract_output_dir(path_config_file_host))
        return res_obj
