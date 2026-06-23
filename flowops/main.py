from typing import Annotated

from sqlalchemy.orm import Session

from flowops.database import get_session

Session = Annotated[Session, get_session]
