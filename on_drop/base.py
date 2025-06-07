from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Callable

import requests


@dataclass
class ProductInfo:
    sku: str
    color: str
    size: str
    in_stock: bool
    additional_info: Optional[Dict[str, Any]] = None


class BasePipeline:
    def __init__(self, steps: List[Callable]):
        self.steps = steps

    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for step in self.steps:
            data = step(data)
        return data


class BaseWebsiteClient(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.pipeline = self.get_pipeline()

    @property
    @abstractmethod
    def website_name(self) -> str:
        """Return the name of the website."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL of the website."""
        pass

    @abstractmethod
    def get_product_url(self, sku: str) -> str:
        """Generate the product URL for the website."""
        pass

    @abstractmethod
    def get_default_headers(self) -> Dict[str, str]:
        """Get the default headers for API requests."""
        pass

    def get_pipeline(self) -> BasePipeline:
        """Get the pipeline for processing requests."""
        return BasePipeline([
            self.prepare_request,
            self.make_request,
            self.parse_response,
            self.extract_stock_info,
            self.create_product_info
        ])

    def prepare_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the request data."""
        data['headers'] = self.get_default_headers()
        data['url'] = self.get_product_url(data['sku'])
        return data

    def make_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make the HTTP request."""
        try:
            response = self.session.get(data['url'], headers=data['headers'])
            response.raise_for_status()
            data['response'] = response.json()
        except Exception as e:
            data['error'] = str(e)
            data['response'] = None
        return data

    @abstractmethod
    def parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the API response."""
        pass

    @abstractmethod
    def extract_stock_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract stock information from parsed data."""
        pass

    def create_product_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final ProductInfo object."""
        data['result'] = ProductInfo(
            sku=data['sku'],
            color=data['color'],
            size=data['size'],
            in_stock=data.get('in_stock', False),
            additional_info=data.get('additional_info')
        )
        return data

    def check_stock(self, sku: str, color: str, size: str) -> ProductInfo:
        """Check stock availability for a product."""
        data = {
            'sku': sku,
            'color': color,
            'size': size
        }
        
        try:
            result = self.pipeline.execute(data)
            return result['result']
        except Exception as e:
            print(f"Error checking {self.website_name} stock for SKU {sku}: {str(e)}")
            return ProductInfo(
                sku=sku,
                color=color,
                size=size,
                in_stock=False
            ) 