import typing
import joblib
import time
import collections
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..logger_unit import logger
from ..operation_module.docker_operation_module import SumoDockerController
from ..operation_module.local_operation_module import LocalSumoController
from ..commons.result_module import SumoResultObjects
from ..commons.sumo_config_obj import SumoConfigObject
from ..file_handler import LocalFileHandler, GcsFileHandler, BaseFileHandler


class BasePipeline(object):
    def __init__(self,
                 file_handler: BaseFileHandler,
                 path_working_dir: typing.Optional[Path] = None,
                 n_jobs: int = 1):
        self.n_jobs = n_jobs
        if path_working_dir is None:
            self.path_working_dir = Path('/tmp').joinpath('sumo_tasks_pipeline').absolute()
        else:
            self.path_working_dir = path_working_dir.absolute()
        # end if
        self.file_handler = file_handler

    @staticmethod
    def check_job_ids(sumo_configs: typing.List[SumoConfigObject]) -> bool:
        seq_job_id = [conf_obj.job_id for conf_obj in sumo_configs]
        counts = collections.Counter(seq_job_id)
        for k, t in counts.items():
            if t > 1:
                raise Exception(f'duplication in job_id = {k}')
        # end for
        return True

    def get_data_directory(self) -> Path:
        raise NotImplementedError()

    def one_simulation(self, sumo_config_object: SumoConfigObject) -> typing.Tuple[str, SumoResultObjects]:
        raise NotImplementedError()

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject]) -> SumoResultObjects:
        raise NotImplementedError()


class LocalSumoPipeline(BasePipeline):
    def __init__(self,
                 file_handler: BaseFileHandler,
                 is_rewrite_windows_path: bool = True,
                 path_working_dir: Path = None,
                 n_jobs: int = 1,
                 sumo_command: str = '/bin/sumo'):
        """A pipeline interface to run SUMO-docker.

        Args:
            path_working_dir: a path to save tmp files.
            n_jobs: the number of cores.
        """
        super(LocalSumoPipeline, self).__init__(path_working_dir=path_working_dir,
                                                n_jobs=n_jobs,
                                                file_handler=file_handler)
        self.sumo_command = sumo_command
        self.is_rewrite_windows_path = is_rewrite_windows_path

    def one_simulation(self, sumo_config_object: SumoConfigObject) -> SumoResultObjects:
        job_status, path = self.file_handler.get_job_status(job_id=sumo_config_object.job_id)
        if job_status == 'finished':
            logger.debug(f'job_id={sumo_config_object.job_id} is already done. Skip it.')
            result_obj = SumoResultObjects(id_scenario=sumo_config_object.scenario_name,
                                           sumo_config_obj=sumo_config_object,
                                           path_output_dir=path)
            return result_obj
        # end if

        sumo_controller = LocalSumoController(sumo_command=self.sumo_command)
        self.file_handler.start_job(sumo_config_object.job_id)
        sumo_result_obj = sumo_controller.start_job(sumo_config=sumo_config_object)
        path_out = self.file_handler.save_file(sumo_config_object.job_id, sumo_result=sumo_result_obj)
        self.file_handler.end_job(sumo_config_object.job_id)
        result_obj = SumoResultObjects(id_scenario=sumo_config_object.scenario_name,
                                       sumo_config_obj=sumo_config_object,
                                       path_output_dir=path_out)
        return result_obj

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject]
                       ) -> typing.List[SumoResultObjects]:
        """Run SUMO simulation.

        Args:
            sumo_configs: List of SUMO Config objects.

        Returns: {scenario-name: `SumoResultObjects`}
        """
        self.check_job_ids(sumo_configs)
        logger.info(f'running sumo simulator now...')
        sumo_result_objects = joblib.Parallel(n_jobs=self.n_jobs)(joblib.delayed(
            self.one_simulation)(conf) for conf in tqdm(sumo_configs))
        logger.info(f'done the simulation.')
        return sumo_result_objects


class DockerPipeline(BasePipeline):
    def __init__(self,
                 file_handler: BaseFileHandler,
                 path_mount_working_dir: Optional[Path] = None,
                 docker_image_name: str = 'kensukemi/sumo-ubuntu18',
                 is_rewrite_windows_path: bool = True,
                 n_jobs: int = 1,
                 time_interval_future_check: float = 3.0,
                 limit_max_wait: float = 3600):
        """A pipeline interface to run SUMO-docker.

        Args:
            file_handler:
            path_mount_working_dir: A path to directory where a container mount as the shared directory.
            docker_image_name: A name of docker-image that you call.
            is_rewrite_windows_path: True, then the class updates Path only when your OS is Windows.
            n_jobs: the number of parallel computations.
            time_interval_future_check: Time interval to check Task status.
            limit_max_wait: Time limit (seconds) to force end process.
        """
        super(DockerPipeline, self).__init__(file_handler=file_handler,
                                             path_working_dir=path_mount_working_dir,
                                             n_jobs=n_jobs)
        self.path_mount_working_dir = self.path_working_dir
        self.docker_image_name = docker_image_name
        self.is_rewrite_windows_path = is_rewrite_windows_path
        self.time_interval_future_check = time_interval_future_check
        self.limit_max_wait = limit_max_wait

    def get_data_directory(self) -> Path:
        return self.path_mount_working_dir

    def one_job(self, sumo_config_obj: SumoConfigObject) -> SumoResultObjects:
        job_status, path = self.file_handler.get_job_status(job_id=sumo_config_obj.job_id)
        if job_status == 'finished':
            logger.debug(f'job_id={sumo_config_obj.job_id} is already done. Skip it.')
            result_obj = SumoResultObjects(id_scenario=sumo_config_obj.scenario_name,
                                           sumo_config_obj=sumo_config_obj,
                                           path_output_dir=path)
            return result_obj
        # end if
        logger.debug(f'running sumo simulator now...')
        time_stamp_current = datetime.utcnow()
        self.file_handler.start_job(sumo_config_obj.job_id)
        sumo_controller = SumoDockerController(
            container_name_base=f'sumo-docker-{sumo_config_obj.scenario_name}-{time_stamp_current}',
            image_name=self.docker_image_name)
        sumo_result_obj = sumo_controller.start_job(sumo_config=sumo_config_obj)
        path_out = self.file_handler.save_file(sumo_config_obj.job_id, sumo_result_obj)
        logger.debug(f'done the simulation.')
        self.file_handler.end_job(sumo_config_obj.job_id)
        return sumo_result_obj

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject]
                       ) -> typing.List[SumoResultObjects]:
        """Run SUMO simulation in a docker container.

        Args:
            sumo_configs: List of SumoConfigObject.
            False raises Exception if there is a destination directory already. Default False.
        Returns:
            dict {scenario-name: `SumoResultObjects`}
        """
        self.check_job_ids(sumo_configs)
        logger.info(f'making the new config files')
        from concurrent.futures import ThreadPoolExecutor
        pool = ThreadPoolExecutor(self.n_jobs)
        s_future_pool = []
        logger.debug(f'starting tasks...')
        for conf in sumo_configs:
            future = pool.submit(self.one_job, (conf))
            s_future_pool.append(future)
        # end for
        logger.debug(f'submitted all tasks.')

        time_at_start = datetime.now()
        logger.debug(f'waiting for task-ends...')
        while True:
            is_end_all = all(f.done() is True for f in s_future_pool)
            if is_end_all:
                break
            time.sleep(self.time_interval_future_check)
            if (datetime.now() - time_at_start).total_seconds() > self.limit_max_wait:
                raise TimeoutError(f'We waited {self.limit_max_wait} seconds. Not finished yet.')
            # end if
        # end while

        d_scenario_name2result = []
        for f_obj in s_future_pool:
            r: SumoResultObjects = f_obj.result()
            d_scenario_name2result.append(r)
        # end for

        return d_scenario_name2result
