from fastapi_utilities import repeat_at
from ..utils.helpers import file_helper


@repeat_at(cron="* * * * *")
def delete_expired():
    file_helper.search_expired_files_and_delete()
    return