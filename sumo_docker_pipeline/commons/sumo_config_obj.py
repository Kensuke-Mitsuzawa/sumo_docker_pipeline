import dataclasses
import pathlib


@dataclasses.dataclass
class SumoConfigObject(object):
    scenario_name: str
    path_config_dir: pathlib.Path
    config_name: str = 'sumo.cfg'

    def __post_init__(self):
        assert self.path_config_dir.exists(), f'No directory found at {self.path_config_dir}'
        assert self.path_config_dir.joinpath(self.config_name).exists()

