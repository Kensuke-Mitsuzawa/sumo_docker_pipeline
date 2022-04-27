import copy
import json
import shutil
import typing
import os

from pathlib import Path
from datetime import datetime


from ..commons.result_module import SumoResultObjects
from .base import BaseFileHandler, SIGNALS


class LocalFileHandler(BaseFileHandler):
    def __init__(self,
                 path_save_root: Path,
                 status_file_name: str = 'status.json',
                 subdir_output: str = 'pipeline-output'):
        self.path_save_root = path_save_root
        assert self.path_save_root.exists()
        self.status_file_name = status_file_name
        self.subdir_output = subdir_output

    def get_job_status(self, job_id: str) -> typing.Tuple[str, Path]:
        path_status = self.path_save_root.joinpath(job_id).joinpath(self.status_file_name)
        if not path_status.exists():
            return 'empty', Path()

        with path_status.open('r') as f:
            signals = json.loads(f.read())
        return signals['status'], Path(self.path_save_root.joinpath(job_id))

    def start_job(self, job_id: str):
        __signals = copy.deepcopy(SIGNALS)
        __signals['started_at'] = datetime.utcnow().isoformat()
        __signals['status'] = 'started'
        self.path_save_root.joinpath(job_id.__str__()).mkdir(exist_ok=True, parents=True)
        with self.path_save_root.joinpath(job_id).joinpath(self.status_file_name).open('w') as f:
            f.write(json.dumps(__signals))

    def end_job(self, job_id: str):
        with self.path_save_root.joinpath(job_id).joinpath(self.status_file_name).open('r') as f:
            signals = json.loads(f.read())

        signals['end_job'] = datetime.utcnow().isoformat()
        signals['status'] = 'finished'
        with self.path_save_root.joinpath(job_id).joinpath(self.status_file_name).open('w') as f:
            f.write(json.dumps(signals))

    def save_file(self, job_id: str, sumo_result: SumoResultObjects) -> Path:
        path_destination = self.path_save_root.joinpath(self.subdir_output).joinpath(job_id)
        shutil.copytree(sumo_result.path_output_dir, path_destination)
        return path_destination
