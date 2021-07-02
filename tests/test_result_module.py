from sumo_docker_pipeline.result_module import SumoResultObjects, MatrixObject
from sumo_docker_pipeline.result_module import ResultFile
from pathlib import Path
import tempfile
import numpy


def test_generate_output(resource_path_root: Path):
    path_output_dir = resource_path_root.joinpath('config_complete/output')
    result_generator = SumoResultObjects(log_message='', path_output_dir=path_output_dir)
    for file_name, res_obj in result_generator.result_files.items():
        for key_name in ['flow', 'speed']:
            matrix_object = res_obj.to_array_objects(key_name)
            assert isinstance(matrix_object, MatrixObject)


def test_parsing_error_out(resource_path_root: Path):
    path_output_dir = resource_path_root.joinpath('error-out.xml')
    result_generator = ResultFile(path_output_dir)
    for attr in result_generator.key_attributes:
        if attr == 'id':
            continue
        # end if
        result_generator.to_array_objects(attr)
    # end for
    speed_matrix = result_generator.to_array_objects('speed')
    __path_temp = Path(tempfile.mktemp())
    __path_temp.mkdir()
    path_temp = __path_temp.joinpath('tmp.npz')
    speed_matrix.to_npz(path_temp)
    restore_matrix = MatrixObject.from_npz(path_temp)
    numpy.all(restore_matrix.matrix == speed_matrix.matrix)


if __name__ == '__main__':
    test_parsing_error_out(Path('./resources'))
    test_generate_output(Path('./resources'))
