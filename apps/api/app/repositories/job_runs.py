from app.models import JobRun
from app.repositories.base import SQLAlchemyRepository


class JobRunRepository(SQLAlchemyRepository[JobRun]):
    model = JobRun
