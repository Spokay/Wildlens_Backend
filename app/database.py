from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session

from app.config import get_settings, logger
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
from app.services.user_service import get_password_hash

settings = get_settings()


def create_database_engine():
    conn_string = settings.database_url

    logger.info(f"Creating database engine: {conn_string}")
    return create_engine(conn_string)


engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_session_for_engine(custom_engine) -> Session:
    return sessionmaker(autocommit=False, autoflush=False, bind=custom_engine)()



def initialize_database():
    logger.info(f"Initializing database for {settings.environment} environment")

    # Environment-specific initialization
    if settings.is_development:
        logger.info("Development: Seeding sample data")
        create_tables(engine)
        seed_data(engine)
    elif settings.is_production:
        logger.info("Production: Database ready")
    elif settings.environment == "testing":
        create_tables(engine)
        seed_data(engine)
        logger.info("Testing: Database ready")


async def startup_database():
    try:
        initialize_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def shutdown_database():
    logger.info("Closing database connections")
    engine.dispose()
    logger.info("Database connections closed")


def get_database_info():
    return {
        "database_url": settings.database_url,
        "is_memory_db": settings.is_using_memory_db,
        "database_type": "SQLite (In-Memory)" if settings.is_using_memory_db else "MariaDB/MySQL",
    }


def create_tables(database_engine):
    logger.info("Creating database and tables")
    SQLModel.metadata.create_all(
        database_engine,
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


def drop_tables(database_engine):
    logger.warning("Dropping all database tables...")
    SQLModel.metadata.drop_all(bind=database_engine)
    logger.info("Database tables dropped")


def seed_data(database_engine):
    logger.info("Seeding data")
    session = get_session_for_engine(database_engine)
    try:
        # add default roles
        role1 = Role(name="ADMIN")
        role2 = Role(name="USER")
        session.add(role1)
        session.add(role2)
        session.commit()
        session.refresh(role1)
        session.refresh(role2)
        session.close()

        criteria_start_test = {"type": "identification_count_by_specie", "required": 0}
        criteria1 = {"type": "identification_count_by_specie", "required": 5}
        criteria2 = {"type": "identification_count_by_specie", "required": 10}

        criteria3 = {"type": "identification_count_by_specie", "required": 5, "specie": 1}
        criteria4 = {"type": "identification_count_by_specie", "required": 10, "specie": 1}

        badge_debut = Badge(
            name="Début de l'aventure",
            description="Il faut bien commencer quelque part !",
            badge_image="https://example.com/chat.jpg",
        )

        badge = Badge(
            name="Explorateur de la nature",
            description="Décerné pour avoir identifié 5 espèces différentes",
            badge_image="https://example.com/chat.jpg",
        )
        badge2 = Badge(
            name="Véteran de la nature",
            description="Décerné pour avoir identifié 10 espèces différentes",
            badge_image="https://example.com/chat.jpg",
        )

        badge3 = Badge(
            name="Amateur de chat",
            description="Décerné pour avoir identifié 5 chats",
            badge_image="https://example.com/chat.jpg",
        )

        badge4 = Badge(
            name="Expert en chat",
            description="Décerné pour avoir identifié 10 chats",
            badge_image="https://example.com/chat.jpg",
        )
        session.add(badge_debut)
        session.add(badge)
        session.add(badge2)
        session.add(badge3)
        session.add(badge4)
        session.commit()
        session.refresh(badge_debut)
        session.refresh(badge)
        session.refresh(badge2)
        session.refresh(badge3)
        session.refresh(badge4)

        badge_criteria_test = BadgeCriteria(badge_id=badge_debut.id, criteria=criteria_start_test)

        badge_criteria = BadgeCriteria(badge_id=badge.id, criteria=criteria1)

        badge_criteria2 = BadgeCriteria(badge_id=badge2.id, criteria=criteria2)

        badge_criteria3 = BadgeCriteria(badge_id=badge3.id, criteria=criteria3)

        badge_criteria4 = BadgeCriteria(badge_id=badge4.id, criteria=criteria4)

        session.add(badge_criteria_test)
        session.add(badge_criteria)
        session.add(badge_criteria2)
        session.add(badge_criteria3)
        session.add(badge_criteria4)
        session.commit()
        session.refresh(badge_criteria_test)
        session.refresh(badge_criteria)
        session.refresh(badge_criteria2)
        session.refresh(badge_criteria3)
        session.refresh(badge_criteria4)
        session.close()

        family1 = Family(
            name="Mammifères",
        )

        specie1 = Specie(
            name="Chat",
            latin_name="Felis catus",
            description="Le chat domestique est un mammifère carnivore de la famille des félidés.",
            size="Petit",
            region="Domestique",
            fun_fact="Les chats peuvent faire des bonds jusqu'à six fois leur taille.",
            specie_exemple_photo="https://example.com/chat.jpg",
            footprint_exemple_photo="https://example.com/chat_pattes.jpg",
            family_id=1,
        )

        password_hashed = get_password_hash("admin123")
        statement = select(User).where(User.email == "admin@admin.fr")
        admin1 = session.exec(statement).first()
        if not admin1:
            admin1 = User(
                username="admin",
                email="admin@admin.fr",
                profile_picture="https://example.com/admin.jpg",
                password=password_hashed,
                role_id=1,
            )
            session.add(admin1)
            session.commit()
            session.refresh(admin1)

        user1 = session.exec(select(User).where(User.email == "user@user.com")).first()
        if not user1:
            user1 = User(
                username="user",
                email="user@user.com",
                profile_picture="https://cdn.unitycms.io/images/04U-s5BHKZn8IFvxj3Fr2N.jpg?op=ocroped&val=1200,800,1000,1000,0,0&sum=cctzliWlDrY",
                password=password_hashed,
                role_id=2,
            )

            session.add(user1)
            session.commit()
            session.refresh(user1)

        session.add(family1)
        session.add(specie1)
        session.commit()
        session.refresh(family1)
        session.refresh(specie1)
        session.close()

    except Exception as e:
        logger.error(f"Failed to seed development data: {e}")
        session.rollback()
    finally:
        session.close()
