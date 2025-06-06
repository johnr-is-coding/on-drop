import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


@dataclass
class ProductInfo:
    sku: str
    color: str
    size: str
    in_stock: bool
    additional_info: Optional[Dict[str, Any]] = None

    
class TheNorthFaceClient():

    BASE_URL = "https://www.thenorthface.com"
    PRODUCT_URL = "https://www.thenorthface.com/api/products/v2/products/{}/inventory"

    @property
    def website_name(self) -> str:
        return "The North Face"

    def get_product_url(self, sku: str) -> str:
        """Generate the product URL for TNF website."""
        return self.PRODUCT_URL.format(sku)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get the required headers for TNF API."""
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
    
    def _parse_stock_status(self, data: Dict[str, Any], size: str, color: str) -> bool:
        """Parse the stock status from API response."""
        try:
            variant_info = self._find_variant_info(data, size, color)
            return variant_info.get("inStock", False)
        except (KeyError, AttributeError):
            return False
    
    def _extract_additional_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional product information."""
        variants = data.get("variants", {})
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
        
        return {
            "product_name": data.get("name"),
            "available_sizes": sorted(list(available_sizes)),
            "stock_status": stock_status
        }
    
    def check_stock(self, sku: str, color: str, size: str) -> ProductInfo:
        """
        Check stock availability for a TNF product.
        
        The North Face API typically requires:
        - SKU format: NF0A88K4
        - Color format: JK3 (color code)
        - Size format: M, L, XL, etc.
        """
        
        # Construct API endpoint
        endpoint = self.PRODUCT_URL.format(sku)
        
        try:
            # Make API request with necessary headers
            response = requests.get(endpoint, headers=self._get_default_headers())
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()  

            in_stock = self._parse_stock_status(data, size, color)
            
            return ProductInfo(
                sku=sku,
                color=color,
                size=size,
                in_stock=in_stock,
            )
            
        except Exception as e:
            # Log error and return product info with in_stock as False
            print(f"Error checking TNF stock for SKU {sku}: {str(e)}")
            return ProductInfo(
                sku=sku,
                color=color,
                size=size,
                in_stock=False
            )
    