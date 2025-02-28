import pytest

from app.services.authentication_service import extract_token_from_request


@pytest.mark.asyncio
async def test_extract_token_from_request_returns_none_if_no_authorization_header_is_provided(
        request_object_with_no_token):
    result = await extract_token_from_request(request_object_with_no_token)

    assert result is None


@pytest.mark.asyncio
async def test_request_exception_should_be_handled_in_middleware_if_no_token_is_provided(client, request_info_with_no_token):
    response = client.request(
        method=request_info_with_no_token["method"],
        url=request_info_with_no_token["url"],
        headers=request_info_with_no_token["headers"],
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_request_exception_should_be_handled_correctly_in_middleware_if_invalid_token_is_provided(client, request_with_invalid_token):
    response = client.request(
        method=request_with_invalid_token["method"],
        url=request_with_invalid_token["url"],
        headers=request_with_invalid_token["headers"],
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


@pytest.mark.asyncio
async def test_user_is_authenticated_after_providing_valid_token(client, request_with_valid_token):
    pass

@pytest.mark.asyncio
async def test_user_is_not_authenticated_if_token_is_expired(client):
    pass
