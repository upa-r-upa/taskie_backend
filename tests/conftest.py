import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from werkzeug.security import generate_password_hash


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.schemas.auth import UserBase
from app.database.db import get_db
from app.models.models import User
from app.core.auth import generate_access_token
from main import app as client_app

engine = create_engine(os.environ.get("TSK_SQLALCHEMY_URL"))
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@pytest.fixture(autouse=True)
def app():
    Base.metadata.create_all(engine)

    yield client_app

    Base.metadata.drop_all(engine)


@pytest.fixture
def session(app: FastAPI):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(app: FastAPI, session: Session):
    def get_db_override():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as client:
        yield client


@pytest.fixture
def user_data() -> UserBase:
    user = UserBase(
        username="test",
        password="test123",
        email="test@test.com",
        grade=1,
        profile_image="test",
        nickname="test",
    )

    return user


@pytest.fixture
def add_user(session: Session, user_data: UserBase) -> User:
    user = User(
        username=user_data.username,
        password=generate_password_hash(user_data.password),
        email=user_data.email,
        grade=user_data.grade,
        profile_image=user_data.profile_image,
        nickname=user_data.nickname,
    )

    session.add(user)
    session.commit()

    yield user


@pytest.fixture
def access_token(user_data: UserBase) -> str:
    return generate_access_token(user_data.username)
