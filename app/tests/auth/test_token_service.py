from datetime import timedelta, timezone, datetime

import jwt
import pytest

from app.services.token_service import create_access_token


@pytest.mark.asyncio
async def test_create_access_token_returns_a_jwt_token_with_expected_data(jwt_secret_key, jwt_expiration_minutes, jwt_algorithm, mocker):
    mocker.patch('app.services.token_service._get_secret_key', return_value=jwt_secret_key)
    mocker.patch('app.services.token_service._get_algorithm', return_value=jwt_algorithm)

    expiration_timedelta = timedelta(minutes=jwt_expiration_minutes)
    expected_expiration_datetime = datetime.now(timezone.utc) + expiration_timedelta

    expected_data = {
        "sub": "exemple@exemple.com",
        "user_id": 1,
        "role_name": "USER",
        "exp": int(expected_expiration_datetime.timestamp()),
    }

    token = await create_access_token(data=expected_data, expires_delta=expiration_timedelta)

    decoded_token = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])

    assert decoded_token["sub"] == expected_data["sub"]
    assert decoded_token["user_id"] == expected_data["user_id"]
    assert decoded_token["role_name"] == expected_data["role_name"]
    assert decoded_token["exp"] == expected_data["exp"]


@pytest.mark.asyncio
async def test_create_access_token_returns_a_jwt_token_with_default_expiration_time(jwt_secret_key, jwt_algorithm, mocker):
    mocker.patch('app.services.token_service._get_secret_key', return_value=jwt_secret_key)
    mocker.patch('app.services.token_service._get_algorithm', return_value=jwt_algorithm)

    expected_expiration_datetime = datetime.now(timezone.utc) + timedelta(minutes=30)

    expected_data = {
        "sub": "exemple@exemple.com",
        "exp": int(expected_expiration_datetime.timestamp()),
    }

    token = await create_access_token(data=expected_data)

    decoded_token = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])

    assert decoded_token["sub"] == expected_data["sub"]
    assert "exp" in decoded_token
    assert decoded_token["exp"] == expected_data["exp"]

