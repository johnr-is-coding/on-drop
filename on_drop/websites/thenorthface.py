from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from on_drop.base import BaseWebsiteClient


@dataclass
class ProductInfo:
    sku: str
    color: str
    size: str
    in_stock: bool
    additional_info: Optional[Dict[str, Any]] = None

    
class TheNorthFaceClient(BaseWebsiteClient):
    @property
    def website_name(self) -> str:
        return "The North Face"

    @property
    def base_url(self) -> str:
        return "https://www.thenorthface.com"

    def get_product_url(self, sku: str) -> str:
        return f"{self.base_url}/api/products/v2/products/{sku}/inventory"

    def get_default_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "x-transaction-id": "811a725b-ae5e-497e-a565-071ff93c7b6a",
            "channel": "ECOMM",
            "locale": "en_US",
            "brand": "TNF",
            "siteid": "TNF-US",
            "source": "ECOM15",
            "region": "NORA"
        }

    def _parse_variant_key(self, variant_key: str) -> Tuple[str, str]:
        """
        Parse a variant key to extract color and size.
        Example: "NF:0A8F5C:CQO:M::1:" -> ("CQO", "M")
        """
        try:
            parts = variant_key.split(":")
            if len(parts) >= 4:
                return parts[2], parts[3]  # color_code, size
            return "", ""
        except (IndexError, AttributeError):
            return "", ""

    def _find_variant_info(self, data: Dict[str, Any], target_size: str, target_color: str) -> Dict[str, Any]:
        """Find the matching variant for the given size and color."""
        variants = data.get("variants", {})
        
        # First try exact match with formatted variant key
        for variant_key, variant_info in variants.items():
            color_code, size = self._parse_variant_key(variant_key)
            if size.upper() == target_size.upper() and color_code.upper() == target_color.upper():
                return variant_info
        
        # If no match found, try basic SKU match (fallback)
        return variants.get(target_color, {})

    def parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the API response."""
        if data.get('response') is None:
            data['parsed_data'] = {}
            return data
            
        data['parsed_data'] = data['response']
        return data

    def extract_stock_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract stock information from parsed data."""
        parsed_data = data.get('parsed_data', {})
        variant_info = self._find_variant_info(parsed_data, data['size'], data['color'])
        
        data['in_stock'] = variant_info.get("inStock", False)
        
        # Extract additional information
        variants = parsed_data.get("variants", {})
        available_sizes = set()
        stock_status = {}
        
        for variant_key, variant_info in variants.items():
            color_code, size = self._parse_variant_key(variant_key)
            if size and variant_info.get("inStock"):
                available_sizes.add(size)
                if color_code:
                    status_key = f"{color_code}_{size}"
                    stock_status[status_key] = {
                        "quantity": variant_info.get("quantity", 0),
                        "status": variant_info.get("stockStatus", "UNKNOWN")
                    }
        
        data['additional_info'] = {
            "product_name": parsed_data.get("name"),
            "available_sizes": sorted(list(available_sizes)),
            "stock_status": stock_status
        }
        
        return data
    