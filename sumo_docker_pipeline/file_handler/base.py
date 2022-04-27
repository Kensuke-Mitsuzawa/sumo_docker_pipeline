from ..commons.result_module import SumoResultObjects

SIGNALS = {
    'started_at': '',
    'end_at': '',
    'status': ''
}


class BaseFileHandler(object):
    def get_job_status(self, job_id: str) -> str:
        raise NotImplementedError()

    def start_job(self, job_id: str):
        raise NotImplementedError()

    def end_job(self, job_id: str):
        raise NotImplementedError()

    def save_file(self, job_id: str, sumo_result: SumoResultObjects):
        raise NotImplementedError()
