import dataclasses

from pathlib import Path
from typing import Dict, Optional

from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject


@dataclasses.dataclass
class ResultFile(object):
    """A handler class that parse output-files of SUMO output.

    Args:
        path_file: pathlib.Path object that leads into output file's path.
        name_file: (optional) file name of the output file.
    """
    path_file: Path
    name_file: Optional[str] = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'ResultFile class for {self.path_file}'

    def __post_init__(self):
        self.name_file = self.path_file.name


@dataclasses.dataclass
class SumoResultObjects(object):
    """A handler class for SUMO's output file(s).

    Args:
        path_output_dir: A directory where your output xmls exist.
        log_message: A log message from SUMO.
        result_files: {output-file-name: `ResultFile`}
    """
    id_scenario: str
    sumo_config_obj: SumoConfigObject
    path_output_dir: Path
    log_message: Optional[str] = None
    result_files: Optional[Dict[str, ResultFile]] = None
