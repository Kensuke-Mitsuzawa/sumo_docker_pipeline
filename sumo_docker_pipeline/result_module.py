import dataclasses
import numpy

from itertools import groupby
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from bs4 import BeautifulSoup

from sumo_docker_pipeline.logger_unit import logger


@dataclasses.dataclass
class MatrixObject(object):
    """
    matrix (2d-array): a 2d-array which contains {value_type}.
    detectors (1d-array): a 1d-array which contains an id of detectors.
    interval_begins (1d-array): a 1d-array which contains a start of an interval-time.
    value_type: name of type that a matrix object has.
    time_interval: length of time-interval.
    """
    matrix: numpy.ndarray
    detectors: numpy.ndarray
    interval_begins: numpy.ndarray
    interval_end: numpy.ndarray
    value_type: str

    def to_npz(self, path_npz: Path):
        dict_obj = dataclasses.asdict(self)
        np.savez(path_npz, **dict_obj)

    @classmethod
    def from_npz(cls, path_npz: Path) -> "MatrixObject":
        data = dict(np.load(str(path_npz), allow_pickle=True))
        return MatrixObject(**data)


@dataclasses.dataclass
class ResultFile(object):
    """A handler class that parse output-files of Sumo's output.

    Args:
        path_file: pathlib.Path object that leads into output file's path.
        name_file: (optional) file name of the output file.
        tree_object: (optional) BeautifulSoup object that bs4 parsed the output xml

    Attributes:
        key_attributes: list object of strings that are available as metric of a matrix.

    Methods:
        to_array_objects: a method to obtain a matrix object.
    """
    path_file: Path
    name_file: Optional[str] = None
    tree_object: Optional[BeautifulSoup] = None
    key_attributes: Optional[List[str]] = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'ResultFile class for {self.path_file}'

    def __post_init__(self):
        self.name_file = self.path_file.name
        self.tree_object = self.load_file()
        self.key_attributes = self.get_attributes(self.tree_object)

    def load_file(self) -> BeautifulSoup:
        f_obj = open(self.path_file, 'r')
        soup = BeautifulSoup(f_obj, 'lxml')
        return soup

    @staticmethod
    def get_attributes(root_soup: BeautifulSoup) -> List[str]:
        __ = []
        for elem in root_soup.find_all('interval'):
            __ += list(elem.attrs.keys())
        # end for
        return list(set(__))

    @staticmethod
    def matrix_with_autofill(matrix_stack: List[List[float]]) -> numpy.ndarray:
        """auto-fill a matrix object with nan value if lengths of lists are different.

        :param matrix_stack: 2nd list. [[value]]
        :return: 2nd ndarray.
        """
        max_length = max([len(l) for l in matrix_stack])
        min_length = min([len(l) for l in matrix_stack])
        if max_length == min_length:
            matrix_value = numpy.array(matrix_stack)
            return matrix_value
        else:
            matrix_value = numpy.zeros([len(matrix_stack), max_length])
            logger.warning('The output file different length of elements. I replaced insufficient values with Nan. '
                           'Be careful the existence of Nan values.')
            matrix_value[:] = np.NAN
            for i, j in enumerate(matrix_stack):
                matrix_value[i][0:len(j)] = j
            # end for
            return matrix_value

    def xml2matrix(self,
                   root_soup: BeautifulSoup,
                   target_element: str) -> MatrixObject:
        """generates matrix object with the specified key name.

        :param root_soup: xml object.
        :param target_element: a name of key which corresponds to values of the matrix.
        :return: MatrixObject
        """
        stacks = []
        __time_interval: Optional[float] = None
        for elem in root_soup.find_all('interval'):
            detector_id = elem.get('id')
            time_begin = float(elem.get('begin'))
            time_end = float(elem.get('end'))

            obj_value = elem.get(target_element)
            try:
                if obj_value == '':
                    target_value = 0.0
                elif obj_value is None:
                    target_value = 0.0
                else:
                    target_value = float(elem.get(target_element))
            except ValueError:
                raise SystemError(f'unexpected error during parsing values because of {obj_value}')
            except KeyError:
                keys = elem.attrs.keys()
                raise KeyError(f'Invalid key name. Available keys are {keys}')
            # end try
            stacks.append([detector_id, time_begin, time_end, target_value])
        # end for
        seq_detector_id = []
        matrix_stack = []
        seq_begin = []
        seq_end = []
        for detector_id, g_obj in groupby(sorted(stacks, key=lambda t: t[0]), key=lambda t: t[0]):
            __ = list(sorted([t for t in g_obj], key=lambda t: t[1]))
            seq_begin = [t[1] for t in __]
            seq_end = [t[2] for t in __]
            seq_value = [t[3] for t in __]
            seq_detector_id.append(detector_id)
            matrix_stack.append(seq_value)
        # end for
        detectors = numpy.array(seq_detector_id)

        begin_time_vector = numpy.array(seq_begin)
        end_time_vector = numpy.array(seq_end)
        matrix_value = self.matrix_with_autofill(matrix_stack)
        assert len(matrix_value.shape) == 2, f'The method expects 2nd array. But it detects {matrix_value.shape} object. ' \
                                             f'Check your xml file at {self.path_file}'
        return MatrixObject(
            matrix=matrix_value,
            detectors=detectors,
            interval_begins=begin_time_vector,
            interval_end=end_time_vector,
            value_type=target_element)

    def to_array_objects(self, aggregation_on: str) -> MatrixObject:
        matrix_obj = self.xml2matrix(root_soup=self.tree_object, target_element=aggregation_on)
        return matrix_obj


@dataclasses.dataclass
class SumoResultObjects(object):
    """A handler class for SUMO's output file(s).

    Args:
        path_output_dir: A directory where your output xmls exist.
        log_message: A log message from SUMO.
        output_file_name: optional if you wanna specify the name of output-xml-file.
        result_files: Not used.

    Attributes:
        result_files: a dict object {output-file-name: ResultFile class}
    """
    path_output_dir: Path
    log_message: Optional[str] = None
    result_files: Optional[Dict[str, ResultFile]] = None
    output_file_name: Optional[str] = None

    def __post_init__(self):
        assert Path(self.path_output_dir).exists()
        if self.output_file_name is not None:
            xml_files = [Path(self.path_output_dir).joinpath(self.output_file_name)]
        else:
            xml_files = list(Path(self.path_output_dir).glob('*xml'))
            assert len(xml_files) > 0, f'No output xml found in {self.path_output_dir}'
        # end if
        self.result_files = {}
        for path_xml in xml_files:
            self.result_files[path_xml.name] = ResultFile(path_xml)
        # end for
