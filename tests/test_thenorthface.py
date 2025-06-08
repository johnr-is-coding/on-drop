import pytest
from unittest.mock import Mock, patch
from on_drop.websites.thenorthface import TheNorthFaceClient

@pytest.fixture
def client():
    return TheNorthFaceClient()


def test_website_properties(client):
    assert client.website_name == "The North Face"
    assert client.base_url == "https://www.thenorthface.com"


def test_get_product_url(client):
    sku = "ABC123"
    expected_url = "https://www.thenorthface.com/api/products/v2/products/ABC123/inventory"
    assert client.get_product_url(sku) == expected_url


def test_get_default_headers(client):
    headers = client.get_default_headers()
    
    assert headers["Accept"] == "application/json"
    assert "User-Agent" in headers
    assert headers["channel"] == "ECOMM"
    assert headers["locale"] == "en_US"
    assert headers["brand"] == "TNF"
    assert headers["siteid"] == "TNF-US"
    assert headers["source"] == "ECOM15"
    assert headers["region"] == "NORA"


def test_parse_variant_key(client):
    # Test valid variant key
    color, size = client._parse_variant_key("NF:0A8F5C:CQO:M::1:")
    assert color == "CQO"
    assert size == "M"
    
    # Test invalid variant key
    color, size = client._parse_variant_key("invalid:key")
    assert color == ""
    assert size == ""
    
    # Test None input
    color, size = client._parse_variant_key(None)
    assert color == ""
    assert size == ""


def test_find_variant_info(client):
    test_data = {
        "variants": {
            "NF:0A8F5C:CQO:M::1:": {
                "inStock": True,
                "quantity": 5
            },
            "NF:0A8F5C:BLK:L::1:": {
                "inStock": False,
                "quantity": 0
            }
        }
    }
    
    # Test exact match
    variant_info = client._find_variant_info(test_data, "M", "CQO")
    assert variant_info["inStock"] is True
    assert variant_info["quantity"] == 5
    
    # Test case insensitive match
    variant_info = client._find_variant_info(test_data, "m", "cqo")
    assert variant_info["inStock"] is True
    
    # Test no match
    variant_info = client._find_variant_info(test_data, "XL", "RED")
    assert variant_info == {}


def test_parse_response(client):
    # Test with valid response
    test_data = {
        "response": {"test": "data"}
    }
    result = client.parse_response(test_data)
    assert result["parsed_data"] == {"test": "data"}
    
    # Test with None response
    test_data = {"response": None}
    result = client.parse_response(test_data)
    assert result["parsed_data"] == {}


def test_extract_stock_info(client):
    test_data = {
        "parsed_data": {
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
        },
        "size": "M",
        "color": "CQO"
    }
    
    result = client.extract_stock_info(test_data)
    
    assert result["in_stock"] is True
    assert "additional_info" in result
    assert result["additional_info"]["product_name"] == "Test Product"
    assert set(result["additional_info"]["available_sizes"]) == {"M", "L"}
    assert "CQO_M" in result["additional_info"]["stock_status"]
    assert result["additional_info"]["stock_status"]["CQO_M"]["quantity"] == 5
    assert result["additional_info"]["stock_status"]["CQO_M"]["status"] == "IN_STOCK"


@patch('requests.Session')
def test_integration_check_stock(mock_session, client):
    # Mock response data
    mock_response = Mock()
    mock_response.json.return_value = {
        "name": "Test Product",
        "variants": {
            "NF:0A8F5C:CQO:M::1:": {
                "inStock": True,
                "quantity": 5,
                "stockStatus": "IN_STOCK"
            }
        }
    }
    mock_session.return_value.get.return_value = mock_response
    client.session = mock_session.return_value
    
    # Test successful stock check
    result = client.check_stock("0A8F5C", "CQO", "M")
    
    assert result.sku == "0A8F5C"
    assert result.color == "CQO"
    assert result.size == "M"
    assert result.in_stock is True
    assert result.additional_info["product_name"] == "Test Product"
    assert result.additional_info["stock_status"]["CQO_M"]["quantity"] == 5


@patch('requests.Session')
def test_integration_check_stock_error(mock_session, client):
    # Mock error response
    mock_session.return_value.get.side_effect = Exception("API Error")
    client.session = mock_session.return_value
    
    # Test error handling
    result = client.check_stock("0A8F5C", "CQO", "M")
    
    assert result.sku == "0A8F5C"
    assert result.color == "CQO"
    assert result.size == "M"
    assert result.in_stock is False
    assert result.additional_info == {'product_name': None, 'available_sizes': [], 'stock_status': {}} 