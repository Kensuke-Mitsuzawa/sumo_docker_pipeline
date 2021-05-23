from sumo_docker_pipeline.result_module import SumoResultObjects, MatrixObject
from pathlib import Path


def test_generate_output(resource_path_root: Path):
    path_output_dir = resource_path_root.joinpath('config_complete/output')
    result_generator = SumoResultObjects(log_message='', path_output_dir=path_output_dir)
    for file_name, res_obj in result_generator.result_files.items():
        for key_name in ['flow', 'speed']:
            matrix_object = res_obj.to_array_objects(key_name)
            assert isinstance(matrix_object, MatrixObject)


if __name__ == '__main__':
    test_generate_output(Path('./resources'))
