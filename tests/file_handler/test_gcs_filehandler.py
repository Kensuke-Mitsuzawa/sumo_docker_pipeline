from sumo_docker_pipeline.file_handler.gcs_filehandler import GcsFileHandler
from sumo_docker_pipeline.static import PATH_PACKAGE_WORK_DIR
from sumo_docker_pipeline.commons.result_module import SumoResultObjects
from sumo_docker_pipeline.commons.sumo_config_obj import SumoConfigObject
from tempfile import mkdtemp
from uuid import uuid4
from pathlib import Path


def test_gcs_filehandler():
    Path(PATH_PACKAGE_WORK_DIR).mkdir(parents=True, exist_ok=True)
    path_local_root = Path(PATH_PACKAGE_WORK_DIR).joinpath(uuid4().__str__())
    path_local_root.mkdir()

    gcs_filehandler = GcsFileHandler(project_name='sumo-cloud-backend',
                                     bucket_name='sumo-docker-pipeline-test')
    gcs_filehandler.start_job('test-job')
    temp_dir = Path(mkdtemp())
    with temp_dir.joinpath('sumo.cfg').open('w') as f:
        f.write('AAAA')
    # end with
    sumo_config = SumoConfigObject(scenario_name='test-job', path_config_dir=temp_dir, config_name='sumo.cfg')
    path_temp_out = Path(PATH_PACKAGE_WORK_DIR).joinpath(uuid4().__str__())
    path_temp_out.mkdir()
    gcs_filehandler.save_file('test-job', SumoResultObjects(id_scenario='test-job',
                                                              sumo_config_obj=sumo_config,
                                                              path_output_dir=path_temp_out))
    status = gcs_filehandler.get_job_status('test-job')
    assert status == 'started'
    gcs_filehandler.end_job('test-job')
    status = gcs_filehandler.get_job_status('test-job')
    assert status == 'finished'


if __name__ == '__main__':
    test_gcs_filehandler()
