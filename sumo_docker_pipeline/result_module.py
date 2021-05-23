import dataclasses
import numpy

from itertools import groupby
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


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


@dataclasses.dataclass
class ResultFile(object):
    path_file: Path
    name_file: Optional[str] = None
    tree_object: Optional[BeautifulSoup] = None
    key_attributes: Optional[List[str]] = None

    def __str__(self):
        return self.path_file

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
    def xml2matrix(root_soup: BeautifulSoup,
                   target_element: str) -> MatrixObject:
        stacks = []
        __time_interval: Optional[float] = None
        for elem in root_soup.find_all('interval'):
            detector_id = elem.get('id')
            time_begin = float(elem.get('begin'))
            time_end = float(elem.get('end'))

            try:
                target_value = float(elem.get(target_element))
            except KeyError:
                keys = elem.attrs.keys()
                raise KeyError(f'Invalid key name. Available keys are {keys}')
            # end try
            stacks.append([detector_id, time_begin, time_end, target_value])
        # end for
        seq_detector_id = []
        matrix_stack = []
        for detector_id, g_obj in groupby(sorted(stacks, key=lambda t: t[0]), key=lambda t: t[0]):
            __ = list(sorted([t for t in g_obj], key=lambda t: t[1]))
            seq_begin = [t[1] for t in __]
            seq_end = [t[2] for t in __]
            seq_value = [t[3] for t in __]
            seq_detector_id.append(detector_id)
            matrix_stack.append(seq_value)
        # end for
        detectors = numpy.array(seq_detector_id)
        matrix_value = numpy.array(matrix_stack)
        begin_time_vector = numpy.array(seq_begin)
        end_time_vector = numpy.array(seq_end)

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
    log_message: str
    path_output_dir: Path
    result_files: Optional[Dict[str, ResultFile]] = None

    def __post_init__(self):
        assert Path(self.path_output_dir).exists()
        xml_files = list(Path(self.path_output_dir).glob('*xml'))
        assert len(xml_files) > 0, f'No output xml found in {self.path_output_dir}'
        self.result_files = {}
        for path_xml in xml_files:
            self.result_files[path_xml.name] = ResultFile(path_xml)
        # end for
