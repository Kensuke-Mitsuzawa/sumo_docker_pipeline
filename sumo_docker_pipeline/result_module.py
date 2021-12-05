import dataclasses

from pathlib import Path
from typing import Dict, List, Optional


from sumo_docker_pipeline.logger_unit import logger



# @dataclasses.dataclass
# class MatrixObject(object):
#     """
#     matrix (2d-array): a 2d-array which contains {value_type}.
#     detectors (1d-array): a 1d-array which contains an id of detectors.
#     interval_begins (1d-array): a 1d-array which contains a start of an interval-time.
#     value_type: name of type that a matrix object has.
#     time_interval: length of time-interval.
#     """
#     matrix: numpy.ndarray
#     detectors: numpy.ndarray
#     interval_begins: numpy.ndarray
#     interval_end: numpy.ndarray
#     value_type: str
#
#     def to_npz(self, path_npz: Path):
#         dict_obj = dataclasses.asdict(self)
#         np.savez(path_npz, **dict_obj)
#
#     @classmethod
#     def from_npz(cls, path_npz: Path) -> "MatrixObject":
#         data = dict(np.load(str(path_npz), allow_pickle=True))
#         return MatrixObject(**data)


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

    def parse_output(self):



@dataclasses.dataclass
class SumoResultObjects(object):
    """A handler class for SUMO's output file(s).

    Args:
        path_output_dir: A directory where your output xmls exist.
        log_message: A log message from SUMO.
        result_files: {output-file-name: `ResultFile`}
    """
    path_output_dir: Path
    log_message: Optional[str] = None
    result_files: Optional[Dict[str, ResultFile]] = None
