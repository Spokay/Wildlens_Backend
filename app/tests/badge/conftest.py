from datetime import datetime

import pytest
from sqlmodel import Session

from app.dto.badge import BadgeResponse
from app.models import Badge, UserBadge, BadgeCriteria, Identification


@pytest.fixture
def mock_session(mocker):
    return mocker.MagicMock(spec=Session)

@pytest.fixture
def mock_badge_not_received():
    return Badge(id=1, name="Test Badge", description="This is a badge that has not yet been received for a user")

@pytest.fixture
def mock_badge_already_received():
    return Badge(id=2, name="Test Badge 2", description="This is a badge that has already been received for a user")

@pytest.fixture
def mock_user_badge_to_award(mock_badge_not_received):
    return UserBadge(user_id=1, badge_id=mock_badge_not_received.id, date_awarded=datetime.now())

@pytest.fixture
def mock_badge_criteria(mock_badge_not_received):
    return BadgeCriteria(
        badge_id=mock_badge_not_received.id,
        criteria={"type": "identification_count_by_specie", "required": 3}
    )

@pytest.fixture
def mock_badge_already_received_response(mock_badge_already_received):
    return BadgeResponse(
        id=mock_badge_already_received.id,
        name=mock_badge_already_received.name,
        description=mock_badge_already_received.description,
        date_awarded=datetime.now()
    )

@pytest.fixture
def mock_badge_and_criteria():
    criteria = {
        "type": "and",
        "conditions": [
            {"type": "identification_count_by_specie", "required": 1, "specie": 1},
            {"type": "identification_count_by_specie", "required": 1, "specie": 2},
        ],
    }
    return BadgeCriteria(badge_id=3, criteria=criteria)

@pytest.fixture
def mock_badge_or_criteria():
    criteria = {
        "type": "or",
        "conditions": [
            {"type": "identification_count_by_specie", "required": 1, "specie": 1},
            {"type": "identification_count_by_specie", "required": 1, "specie": 2},
        ],
    }
    return BadgeCriteria(badge_id=4, criteria=criteria)

@pytest.fixture
def mock_identification():
    return Identification(user_id=1, specie_id=1)