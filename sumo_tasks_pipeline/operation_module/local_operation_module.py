from pathlib import Path, WindowsPath
import subprocess
import shutil
from sumo_tasks_pipeline.logger_unit import logger
from sumo_tasks_pipeline.operation_module.base_operation import BaseController
from sumo_tasks_pipeline.commons.sumo_config_obj import SumoConfigObject
from sumo_tasks_pipeline.commons.result_module import SumoResultObjects


class LocalSumoController(BaseController):
    def __init__(self,
                 sumo_command: str = None,
                 is_rewrite_windows_path: bool = True,
                 is_copy_config_dir: bool = True,
                 is_compress_result: bool = False,
                 default_archive_format: str = 'bztar'):
        """

        Args:
            sumo_command: Path to the SUMO command.
            is_rewrite_windows_path: Automatic path fix for Windows.
            is_copy_config_dir: True; run SUMO simulation AFTER copy the original config file to tmp directory; False NOT.
            is_compress_result: True; Compress the result with tar.zip (deleting the uncompressed directory). False; not compress the directory nor delete it.
        """
        if sumo_command is None:
            sumo_command = shutil.which('sumo')
            if sumo_command is None:
                raise Exception('command `sumo` is NOT found in your system. Check your environment. '
                                'or, give path to sumo manually. Use the `sumo_command` argument.')

        super(LocalSumoController, self).__init__(
            sumo_command=sumo_command,
            is_rewrite_windows_path=is_rewrite_windows_path,
            is_copy_config_dir=is_copy_config_dir,
            is_compress_result=is_compress_result,
            default_archive_format=default_archive_format
        )
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

    def start_job(self, sumo_config: SumoConfigObject) -> SumoResultObjects:
        """Run SUMO on local.

        Args:
            target_scenario_name: Nothing. Keep it None.
            config_file_name: "sumo.cfg" name.

        Returns: `SumoResultObjects`
        """
        sumo_config = self.copy_config_file(sumo_config, is_copy_config_dir=self.is_copy_config_dir)
        if self.is_rewrite_windows_path and isinstance(sumo_config.path_config_dir, WindowsPath):
            # If windows...Path structure is broken. Fix it manually.
            path_config_file = sumo_config.path_config_dir.as_posix()
        else:
            path_config_file = sumo_config.path_config_dir.joinpath(sumo_config.config_name)
        # end if

        job_command = f'{self.sumo_command} -c {path_config_file}'
        logger.debug(f'executing job with command {job_command}')

        sumo_bash_command = [self.sumo_command, '-c', path_config_file]
        pipe_obj = subprocess.Popen(sumo_bash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = pipe_obj.communicate()
        r_code = pipe_obj.returncode
        assert r_code == 0

        res_obj = self.pack_sumo_result(sumo_config, outs)
        return res_obj
