from google.cloud import storage
from pathlib import Path

import typing
import copy
import google
import os
import json
import glob
from datetime import datetime
from google.oauth2 import service_account
from .base import BaseFileHandler, SIGNALS
from ..commons.result_module import SumoResultObjects
from ..static import PATH_PACKAGE_WORK_DIR


class GcsFileHandler(BaseFileHandler):
    def __init__(self,
                 project_name: str,
                 bucket_name: str,
                 path_credential: typing.Optional[Path] = None,
                 status_file_name: str = 'status.json',
                 subdir_output: str = 'output'):
        self.path_credential = path_credential
        credentials = self.get_credentials()
        self.storage_client = storage.Client(project=project_name, credentials=credentials)
        self.bucket_name = bucket_name
        self.status_file_name = status_file_name
        self.subdir_output = subdir_output

    def get_credentials(self) -> google.auth.credentials.Credentials:
        if self.path_credential is None:
            assert os.environ["GOOGLE_APPLICATION_CREDENTIALS"] is not None, \
                'GOOGLE_APPLICATION_CREDENTIALS should be set.'
            self.path_credential = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            credentials = service_account.Credentials.from_service_account_file(
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
            return credentials
        else:
            credentials = service_account.Credentials.from_service_account_file(
                self.path_credential.__str__())
            return credentials

    def create_bucket(self):
        bucket = self.storage_client.create_bucket(self.bucket_name)

    def get_job_status(self, job_id: str) -> typing.Tuple[str, Path]:
        path_local = Path(PATH_PACKAGE_WORK_DIR).joinpath(job_id)
        bucket = self.storage_client.get_bucket(self.bucket_name)
        file_name = f"{self.subdir_output}/{job_id}/" + self.status_file_name
        blob = bucket.blob(file_name)
        blob.download_to_filename(path_local.joinpath(self.status_file_name))

        stats = storage.Blob(bucket=bucket, name=file_name).exists(self.storage_client)
        if stats is False:
            return 'empty', Path()

        with path_local.joinpath(self.status_file_name).open('r') as f:
            signals = json.loads(f.read())
        return signals['status'], Path(f"{self.subdir_output}/{job_id}/")

    def start_job(self, job_id: str):
        __signals = copy.deepcopy(SIGNALS)
        __signals['started_at'] = datetime.utcnow().isoformat()
        __signals['status'] = 'started'

        # save on local
        path_local = Path(PATH_PACKAGE_WORK_DIR).joinpath(job_id)
        path_local.mkdir(exist_ok=True)
        with path_local.joinpath(self.status_file_name).open('w') as f:
            f.write(json.dumps(__signals))

        # save on GCS
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(f"{self.subdir_output}/{job_id}/" + self.status_file_name)
        blob.upload_from_filename(path_local.joinpath(self.status_file_name))

    def end_job(self, job_id: str):
        path_local = Path(PATH_PACKAGE_WORK_DIR).joinpath(job_id)

        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(f"{self.subdir_output}/{job_id}/" + self.status_file_name)
        blob.download_to_filename(path_local.joinpath(self.status_file_name))

        # get status file from gcs
        with path_local.joinpath(self.status_file_name).open('r') as f:
            signals = json.loads(f.read())

        signals['end_job'] = datetime.utcnow().isoformat()
        signals['status'] = 'finished'
        with path_local.joinpath(self.status_file_name).open('w') as f:
            f.write(json.dumps(signals))

        # upload to GCS
        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(f"{self.subdir_output}/{job_id}/" + self.status_file_name)
        blob.upload_from_filename(path_local.joinpath(self.status_file_name))

    def save_file(self, job_id: str, sumo_result: SumoResultObjects) -> Path:
        bucket = self.storage_client.get_bucket(self.bucket_name)
        for local_file in glob.glob(sumo_result.path_output_dir.as_posix() + '/**'):
            filename = local_file.split('/')[-1]
            blob = bucket.blob(f"{self.subdir_output}/{job_id}" + filename)
            blob.upload_from_filename(local_file)
        # end for
        return Path(f"{self.subdir_output}/{job_id}")
