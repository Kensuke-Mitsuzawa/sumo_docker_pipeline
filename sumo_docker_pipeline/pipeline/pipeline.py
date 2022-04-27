import typing
import joblib
from datetime import datetime
from pathlib import Path
from typing import Optional
from sumo_docker_pipeline.logger_unit import logger
from sumo_docker_pipeline.operation_module.docker_operation_module import SumoDockerController
from sumo_docker_pipeline.operation_module.local_operation_module import LocalSumoController
from sumo_docker_pipeline.commons.result_module import SumoResultObjects
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
import time


class BasePipeline(object):
    def __init__(self,
                 path_working_dir: typing.Optional[Path] = None,
                 n_jobs: int = 1):
        self.n_jobs = n_jobs
        if path_working_dir is None:
            self.path_working_dir = Path('/tmp').joinpath('sumo_docker_pipeline').absolute()
        else:
            self.path_working_dir = path_working_dir.absolute()
        # end if

    def get_data_directory(self) -> Path:
        raise NotImplementedError()

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject],
                       is_overwrite: bool = False) -> SumoResultObjects:
        raise NotImplementedError()


class LocalSumoPipeline(BasePipeline):
    def __init__(self,
                 is_rewrite_windows_path: bool = True,
                 path_working_dir: Path = None,
                 n_jobs: int = 1,
                 sumo_command: str = '/bin/sumo'):
        """A pipeline interface to run SUMO-docker.

        Args:
            path_working_dir: a path to save tmp files.
            n_jobs: the number of cores.
        """
        super(LocalSumoPipeline, self).__init__(path_working_dir=path_working_dir, n_jobs=n_jobs)
        self.sumo_command = sumo_command

        # todo move Template2SuMoConfig to other module.
        # self.template_generator = Template2SuMoConfig(path_config_file=str(path_config_file),
        #                                               path_destination_dir=str(path_destination_scenario))
        self.is_rewrite_windows_path = is_rewrite_windows_path

    def one_simulation(self, sumo_config_object: SumoConfigObject) -> typing.Tuple[str, SumoResultObjects]:
        sumo_controller = LocalSumoController(sumo_command=self.sumo_command)
        sumo_result_obj = sumo_controller.start_job(sumo_config=sumo_config_object)
        return sumo_config_object.scenario_name, sumo_result_obj

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject],
                       is_overwrite: bool = False) -> typing.Dict[str, SumoResultObjects]:
        """Run SUMO simulation.

        Args:
            sumo_configs: List of SUMO Config objects.
            is_overwrite: True, then the method overwrites outputs from SUMO. False raises Exception if there is a destination directory already. Default False.

        Returns: {scenario-name: `SumoResultObjects`}
        """
        logger.info(f'running sumo simulator now...')
        sumo_result_objects = joblib.Parallel(n_jobs=self.n_jobs)(joblib.delayed(
            self.one_simulation)(conf) for conf in sumo_configs)
        logger.info(f'done the simulation.')
        _ = dict(sumo_result_objects)
        return _


class DockerPipeline(BasePipeline):
    def __init__(self,
                 path_mount_working_dir: Optional[Path] = None,
                 docker_image_name: str = 'kensukemi/sumo-ubuntu18',
                 is_rewrite_windows_path: bool = True,
                 n_jobs: int = 1,
                 time_interval_future_check: float = 3.0,
                 limit_max_wait: float = 3600):
        """A pipeline interface to run SUMO-docker.

        Args:
            The other config files should be in the same directory (or under the sub-directory)
            path_mount_working_dir: A path to directory where a container mount as the shared directory.
            docker_image_name: A name of docker-image that you call.
            is_rewrite_windows_path: True, then the class updates Path only when your OS is Windows.
            n_jobs: the number of parallel computations.
            time_interval_future_check: Time interval to check Task status.
            limit_max_wait: Time limit (seconds) to force end process.
        """
        super(DockerPipeline, self).__init__(path_working_dir=path_mount_working_dir, n_jobs=n_jobs)
        self.path_mount_working_dir = self.path_working_dir
        self.docker_image_name = docker_image_name
        self.is_rewrite_windows_path = is_rewrite_windows_path
        self.time_interval_future_check = time_interval_future_check
        self.limit_max_wait = limit_max_wait

    def get_data_directory(self) -> Path:
        return self.path_mount_working_dir

    def one_job(self, sumo_config_obj: SumoConfigObject) -> SumoResultObjects:
        logger.debug(f'running sumo simulator now...')
        time_stamp_current = datetime.now().timestamp()
        sumo_controller = SumoDockerController(
            container_name_base=f'sumo-docker-{sumo_config_obj.scenario_name}-{time_stamp_current}',
            image_name=self.docker_image_name,
        )
        sumo_result_obj = sumo_controller.start_job(sumo_config=sumo_config_obj)
        logger.debug(f'done the simulation.')
        return sumo_result_obj

    def run_simulation(self,
                       sumo_configs: typing.List[SumoConfigObject],
                       is_overwrite: bool = False) -> typing.Dict[str, SumoResultObjects]:
        """Run SUMO simulation in a docker container.

        Args:
            sumo_configs: List of SumoConfigObject.
            is_overwrite: True, then the method overwrites outputs from SUMO.
            False raises Exception if there is a destination directory already. Default False.
        Returns:
            dict {scenario-name: `SumoResultObjects`}
        """
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

        d_scenario_name2result = {}
        for f_obj in s_future_pool:
            r: SumoResultObjects = f_obj.result()
            d_scenario_name2result[r.id_scenario] = r
        # end for
        return d_scenario_name2result
