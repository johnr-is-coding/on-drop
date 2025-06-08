import pytest
from unittest.mock import Mock, patch
from on_drop.base import BasePipeline, BaseWebsiteClient, ProductInfo

def test_base_pipeline():
    # Test pipeline execution
    def step1(data): 
        data['step1'] = True
        return data
    
    def step2(data):
        data['step2'] = True
        return data
    
    pipeline = BasePipeline([step1, step2])
    result = pipeline.execute({'initial': True})
    
    assert result['initial'] is True
    assert result['step1'] is True
    assert result['step2'] is True


class MockWebsiteClient(BaseWebsiteClient):
    @property
    def website_name(self):
        return "Mock Website"
    
    @property
    def base_url(self):
        return "https://mock.com"
    
    def get_product_url(self, sku):
        return f"{self.base_url}/product/{sku}"
    
    def get_default_headers(self):
        return {"User-Agent": "Mock"}
    
    def parse_response(self, data):
        if 'error' in data:
            data['parsed_data'] = {}
            return data
        data['parsed'] = True
        return data
    
    def extract_stock_info(self, data):
        if 'error' in data:
            data['in_stock'] = False
            return data
        data['in_stock'] = True
        return data


@pytest.fixture
def mock_client():
    return MockWebsiteClient()


def test_base_website_client_prepare_request(mock_client):
    data = {'sku': '12345'}
    result = mock_client.prepare_request(data)
    
    assert result['headers'] == {"User-Agent": "Mock"}
    assert result['url'] == "https://mock.com/product/12345"


@patch('requests.Session')
def test_base_website_client_make_request(mock_session, mock_client):
    # Setup mock response
    mock_response = Mock()
    mock_response.json.return_value = {"test": "data"}
    mock_session.return_value.get.return_value = mock_response
    mock_client.session = mock_session.return_value
    
    data = {
        'url': 'https://mock.com/product/12345',
        'headers': {"User-Agent": "Mock"}
    }
    
    result = mock_client.make_request(data)
    assert result['response'] == {"test": "data"}


@patch('requests.Session')
def test_base_website_client_make_request_error(mock_session, mock_client):
    # Setup mock response to raise an error
    mock_session.return_value.get.side_effect = Exception("Test error")
    mock_client.session = mock_session.return_value
    
    data = {
        'url': 'https://mock.com/product/12345',
        'headers': {"User-Agent": "Mock"}
    }
    
    result = mock_client.make_request(data)
    assert result['error'] == "Test error"
    assert result['response'] is None


def test_base_website_client_create_product_info(mock_client):
    data = {
        'sku': '12345',
        'color': 'red',
        'size': 'M',
        'in_stock': True,
        'additional_info': {'test': 'info'}
    }
    
    result = mock_client.create_product_info(data)
    product_info = result['result']
    
    assert isinstance(product_info, ProductInfo)
    assert product_info.sku == '12345'
    assert product_info.color == 'red'
    assert product_info.size == 'M'
    assert product_info.in_stock is True
    assert product_info.additional_info == {'test': 'info'}


@patch('requests.Session')
def test_base_website_client_check_stock(mock_session, mock_client):
    # Test successful stock check
    mock_response = Mock()
    mock_response.json.return_value = {"test": "data"}
    mock_session.return_value.get.return_value = mock_response
    mock_client.session = mock_session.return_value
    
    result = mock_client.check_stock('12345', 'red', 'M')
    
    assert isinstance(result, ProductInfo)
    assert result.sku == '12345'
    assert result.color == 'red'
    assert result.size == 'M'
    assert result.in_stock is True


@patch('requests.Session')
def test_base_website_client_check_stock_error(mock_session, mock_client):
    # Test error handling in stock check
    mock_session.return_value.get.side_effect = Exception("Test error")
    mock_client.session = mock_session.return_value
    
    result = mock_client.check_stock('12345', 'red', 'M')
    
    assert isinstance(result, ProductInfo)
    assert result.sku == '12345'
    assert result.color == 'red'
    assert result.size == 'M'
    assert result.in_stock is False
    assert result.additional_info is None 