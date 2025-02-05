import pytest
from fastapi import HTTPException

from app.services.authentication_service import extract_token_from_request


@pytest.mark.asyncio
async def test_extract_token_from_request_returns_none_if_no_authorization_header_is_provided(request_object_with_no_token):

    result = await extract_token_from_request(request_object_with_no_token)

    assert result is None

@pytest.mark.asyncio
async def test_any_request_should_return_401_if_no_token_is_provided(client, request_info_with_no_token):

    with pytest.raises(HTTPException):
        response = await client.request(
            method=request_info_with_no_token["method"],
            url=request_info_with_no_token["url"],
            headers=request_info_with_no_token["headers"],
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_any_request_should_return_401_if_invalid_token_is_provided(client):
    pass


@pytest.mark.asyncio
async def test_user_is_authenticated_after_providing_valid_token(client):
    pass


@pytest.mark.asyncio
async def test_user_is_not_authenticated_if_token_is_expired(client):
    pass

