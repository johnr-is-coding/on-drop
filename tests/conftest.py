import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_response():
    """Create a mock response object with json method."""
    response = Mock()
    response.json.return_value = {"test": "data"}
    return response


@pytest.fixture
def sample_variant_data():
    """Sample variant data for testing."""
    return {
        "name": "Test Product",
        "variants": {
            "NF:0A8F5C:CQO:M::1:": {
                "inStock": True,
                "quantity": 5,
                "stockStatus": "IN_STOCK"
            },
            "NF:0A8F5C:CQO:L::1:": {
                "inStock": True,
                "quantity": 3,
                "stockStatus": "IN_STOCK"
            },
            "NF:0A8F5C:BLK:M::1:": {
                "inStock": False,
                "quantity": 0,
                "stockStatus": "OUT_OF_STOCK"
            }
        }
    } 