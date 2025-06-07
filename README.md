# On Drop

A Python package for checking product availability across different websites. The package uses a pipeline pattern and a base class structure that makes it easy to add support for new websites.

## Features

- Pipeline-based processing of stock checking requests
- Extensible base class for adding new website support
- Clean and consistent interface across different websites
- Detailed product information including stock status and available sizes

## Installation

```bash
pip install on-drop
```

Or using Poetry:

```bash
poetry install
```

## Usage

### Command Line Interface

```bash
# Check stock for a product on The North Face website
on-drop NF0A88K4 JK3 M --store TNF

# Check stock for a product on another supported website
on-drop <sku> <color> <size> --store <store-code>
```

### Python API

```python
from on_drop.websites.thenorthface import TheNorthFaceClient

# Create a client instance
client = TheNorthFaceClient()

# Check stock
result = client.check_stock(
    sku="NF0A88K4",    # Product SKU
    color="JK3",       # Color code
    size="M"           # Size code
)

# Access results
print(f"In Stock: {result.in_stock}")
print(f"Additional Info: {result.additional_info}")
```

## Adding Support for New Websites

1. Create a new file in the `websites` directory for your website
2. Create a new class that extends `BaseWebsiteClient`
3. Implement the required abstract methods:
   - `website_name`
   - `base_url`
   - `get_product_url`
   - `get_default_headers`
   - `parse_response`
   - `extract_stock_info`

Example:

```python
from typing import Any, Dict
from on_drop.base import BaseWebsiteClient

class NewWebsiteClient(BaseWebsiteClient):
    @property
    def website_name(self) -> str:
        return "New Website"

    @property
    def base_url(self) -> str:
        return "https://api.newwebsite.com"

    def get_product_url(self, sku: str) -> str:
        return f"{self.base_url}/products/{sku}/stock"

    def get_default_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0..."
        }

    def parse_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data['parsed_data'] = data['response']
        return data

    def extract_stock_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        parsed_data = data['parsed_data']
        data['in_stock'] = parsed_data.get('inStock', False)
        data['additional_info'] = {
            'product_name': parsed_data.get('name'),
            'available_sizes': parsed_data.get('sizes', [])
        }
        return data
```

4. Add your client to the `WEBSITE_CLIENTS` dictionary in `main.py`

## Pipeline Steps

The default pipeline includes these steps:

1. `prepare_request`: Prepares the HTTP request with headers and URL
2. `make_request`: Makes the actual HTTP request to the website
3. `parse_response`: Parses the raw response into a structured format
4. `extract_stock_info`: Extracts stock information from the parsed data
5. `create_product_info`: Creates the final ProductInfo object

You can customize the pipeline by overriding the `get_pipeline` method in your website client class.

## Development

To set up the development environment:

```bash
# Install dependencies including development packages
poetry install

# Run type checking
poetry run mypy .

# Run the CLI
poetry run on-drop <sku> <color> <size> --store TNF
```

## License

MIT
