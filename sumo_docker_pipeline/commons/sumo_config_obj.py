import dataclasses
import pathlib
import typing


@dataclasses.dataclass
class SumoConfigObject(object):
    scenario_name: str
    path_config_dir: pathlib.Path
    config_name: str = 'sumo.cfg'
    path_config_dir_original: typing.Optional[pathlib.Path] = None
    job_id: typing.Optional[str] = None

    def __post_init__(self):
        assert self.path_config_dir.exists(), f'No directory found at {self.path_config_dir}'
        assert self.path_config_dir.joinpath(self.config_name).exists()
        if self.job_id is None:
            self.job_id = self.scenario_name
        else:
            self.job_id = self.job_id


