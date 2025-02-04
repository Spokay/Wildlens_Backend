from datetime import datetime

import pytest

from app.dto.badge import BadgeResponse
from app.models import UserBadge
from app.services.badge_service import (
    get_user_badges,
    get_badges_already_received,
    get_criteria_for_unawarded_badges,
    award_badge,
    evaluate_identification_count_by_specie,
    evaluate_criteria,
)

@pytest.mark.asyncio
async def test_get_badges_already_received(mock_session, mock_badge_already_received):
    # Arrange
    user_id = 1
    mock_session.exec.return_value.all.return_value = [(mock_badge_already_received, datetime.now())]

    # Act
    result = await get_badges_already_received(user_id, mock_session)

    # Assert
    assert len(result) == 1
    assert isinstance(result[0], BadgeResponse)
    mock_session.exec.assert_called_once()

@pytest.mark.asyncio
async def test_get_criteria_for_unawarded_badges(mock_session, mock_badge_criteria, mock_badge_already_received, mock_badge_not_received):
    # Arrange
    awarded_badge_ids = {mock_badge_already_received.id}
    mock_session.exec.return_value.all.return_value = [mock_badge_criteria]

    # Act
    result = await get_criteria_for_unawarded_badges(awarded_badge_ids, mock_session)

    # Assert
    assert len(result) == 1
    assert result[0].badge_id == mock_badge_not_received.id
    mock_session.exec.assert_called_once()

@pytest.mark.asyncio
async def test_award_badge(mock_session, mock_user_badge_to_award):
    # Arrange
    user_id = 1
    badge_id = 1
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    result = await award_badge(user_id, badge_id, mock_session)

    # Assert
    assert isinstance(result, UserBadge)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_evaluate_identification_count_by_specie(mock_session):
    # Arrange
    user_id = 1
    criteria = {"type": "identification_count_by_specie", "required": 1, "specie": 1}
    mock_session.exec.return_value.one.return_value = 1

    # Act
    result = await evaluate_identification_count_by_specie(user_id, criteria, mock_session)
    print(result)

    # Assert
    assert result is True
    mock_session.exec.assert_called_once()

@pytest.mark.asyncio
async def test_evaluate_criteria_and_type(mock_session, mock_badge_and_criteria):
    # Arrange
    user_id = 1
    criteria = mock_badge_and_criteria.criteria
    mock_session.exec.return_value.one.side_effect = [1, 1]

    # Act
    result = await evaluate_criteria(user_id, criteria, mock_session)

    # Assert
    assert result is True
    assert mock_session.exec.call_count == 2

@pytest.mark.asyncio
async def test_evaluate_criteria_or_type(mock_session, mock_badge_or_criteria):
    # Arrange
    user_id = 1
    criteria = mock_badge_or_criteria.criteria
    mock_session.exec.return_value.one.side_effect = [0, 1]

    # Act
    result = await evaluate_criteria(user_id, criteria, mock_session)

    # Assert
    assert result is True
    assert mock_session.exec.call_count == 2

@pytest.mark.asyncio
async def test_evaluate_criteria_unknown_type(mock_session):
    # Arrange
    user_id = 1
    criteria = {"type": "unknown_type"}

    # Act & Assert
    with pytest.raises(ValueError, match="Unknown criteria type: unknown_type"):
        await evaluate_criteria(user_id, criteria, mock_session)

@pytest.mark.asyncio
async def test_get_user_badges_returns_already_awarded_badges_and_newly_received_ones(
        mock_session,
        mock_badge_not_received,
        mock_badge_criteria,
        mock_user_badge_to_award,
        mock_badge_already_received_response,
        mocker
):
    # Arrange
    user_id = 1
    badges_already_received = [mock_badge_already_received_response]

    get_badges_already_received_mock = mocker.patch(
        "app.services.badge_service.get_badges_already_received",
        return_value=badges_already_received
    )

    unawarded_badge_criteria = [mock_badge_criteria]
    get_criteria_for_unawarded_badges_mock = mocker.patch(
        "app.services.badge_service.get_criteria_for_unawarded_badges",
        return_value=unawarded_badge_criteria
    )

    evaluate_criteria_mock = mocker.patch(
        "app.services.badge_service.evaluate_criteria",
        return_value=True
    )

    award_badge_mock = mocker.patch(
        "app.services.badge_service.award_badge",
        return_value=mock_user_badge_to_award
    )

    mock_session.get.return_value = mock_badge_not_received

    # Act
    result = await get_user_badges(user_id, mock_session)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], BadgeResponse)
    assert isinstance(result[1], BadgeResponse)

    get_badges_already_received_mock.assert_called_once_with(user_id, mock_session)

    get_criteria_for_unawarded_badges_mock.assert_called_once_with(
        {mock_badge_already_received_response.id},
        mock_session
    )

    evaluate_criteria_mock.assert_called_once_with(
        user_id, mock_badge_criteria.criteria, mock_session
    )

    award_badge_mock.assert_called_once_with(
        user_id, mock_badge_criteria.badge_id, mock_session
    )