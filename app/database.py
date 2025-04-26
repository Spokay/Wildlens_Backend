import os

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from app.models import (
    Role,
    Family,
    Habitat,
    Specie,
    User,
    Badge,
    UserBadge,
    SpecieHabitat,
    Identification,
    BadgeCriteria,
)

host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", 3306)
database = os.getenv("DB_NAME", "")
user = os.getenv("DB_USER", "")
password = os.getenv("DB_PASSWORD", "")

conn_string = f"mariadb+pymysql://{user}:{password}@{host}:{port}/{database}"

database_engine = create_engine(conn_string)


def get_session():
    with Session(database_engine) as session:
        try:
            yield session
        finally:
            session.close()


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Role.__table__,
            Family.__table__,
            Habitat.__table__,
            Specie.__table__,
            User.__table__,
            Badge.__table__,
            UserBadge.__table__,
            SpecieHabitat.__table__,
            Identification.__table__,
            BadgeCriteria.__table__,
        ],
        checkfirst=True,
    )

    # add default roles
    with Session(engine) as session:
        role1 = Role(name="ADMIN")
        role2 = Role(name="USER")
        session.add(role1)
        session.add(role2)
        session.commit()
        session.refresh(role1)
        session.refresh(role2)
        session.close()

    # session = Session(engine)
    #
    # criteria1 = {
    #     "type": "identification_count_by_specie",
    #     "required": 5
    # }
    # criteria2 = {
    #     "type": "identification_count_by_specie",
    #     "required": 10
    # }
    #
    # criteria3 = {
    #     "type": "identification_count_by_specie",
    #     "required": 5,
    #     "specie": 1
    # }
    # criteria4 = {
    #     "type": "identification_count_by_specie",
    #     "required": 10,
    #     "specie": 1
    # }
    #
    # badge = Badge(
    #     name="Explorateur de la nature",
    #     description="Décerné pour avoir identifié 5 espèces différentes"
    # )
    # badge2 = Badge(
    #     name="Véteran de la nature",
    #     description="Décerné pour avoir identifié 10 espèces différentes"
    # )
    #
    # badge3 = Badge(
    #     name="Amateur de chat",
    #     description="Décerné pour avoir identifié 5 chats"
    # )
    #
    # badge4 = Badge(
    #     name="Expert en chat",
    #     description="Décerné pour avoir identifié 10 chats"
    # )
    # session.add(badge)
    # session.add(badge2)
    # session.add(badge3)
    # session.add(badge4)
    # session.commit()
    # session.refresh(badge)
    # session.refresh(badge2)
    # session.refresh(badge3)
    # session.refresh(badge4)
    #
    # badge_criteria = BadgeCriteria(
    #     badge_id=badge.id,
    #     criteria=criteria1
    # )
    #
    # badge_criteria2 = BadgeCriteria(
    #     badge_id=badge2.id,
    #     criteria=criteria2
    # )
    #
    # badge_criteria3 = BadgeCriteria(
    #     badge_id=badge3.id,
    #     criteria=criteria3
    # )
    #
    # badge_criteria4 = BadgeCriteria(
    #     badge_id=badge4.id,
    #     criteria=criteria4
    # )
    #
    # session.add(badge_criteria)
    # session.add(badge_criteria2)
    # session.add(badge_criteria3)
    # session.add(badge_criteria4)
    # session.commit()
    # session.refresh(badge_criteria)
    # session.refresh(badge_criteria2)
    # session.refresh(badge_criteria3)
    # session.refresh(badge_criteria4)
    # session.close()
