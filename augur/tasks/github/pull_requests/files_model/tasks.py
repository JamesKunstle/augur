import logging
import traceback
from augur.application.db.session import DatabaseSession
from augur.tasks.github.pull_requests.files_model.core import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.util import execute_session_query

@celery.task()
def process_pull_request_files(repo_git: str) -> None:

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(process_pull_request_files.__name__)

    with GithubTaskSession(logger, engine) as session:
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo = execute_session_query(query, 'one')
        try:
            pull_request_files_model(repo.repo_id, logger, session)
        except Exception as e:
            logger.error(f"Could not complete pull_request_files_model!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            #raise e