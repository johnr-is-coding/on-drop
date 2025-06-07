import click

from on_drop.websites.thenorthface import TheNorthFaceClient


WEBSITE_CLIENTS = {
    'TNF': TheNorthFaceClient,
}


@click.command()
@click.argument("sku")
@click.argument("color")
@click.argument("size")
@click.option("--store", "-s", default="TNF", help="Store name, default is 'TNF'")
def main(store: str, sku: str, color: str, size: str):
    """Check product availability across different websites."""
    if store not in WEBSITE_CLIENTS:
        print(f"Error: Store '{store}' not supported. Available stores: {', '.join(WEBSITE_CLIENTS.keys())}")
        return

    client_class = WEBSITE_CLIENTS[store]
    client = client_class()
    result = client.check_stock(sku=sku, color=color, size=size)
    
    print(f"\nChecking {client.website_name} stock for SKU {sku}:")
    print(f"Size: {size}")
    print(f"Color: {color}")
    print(f"In Stock: {result.in_stock}")
    
    if result.additional_info:
        print("\nAdditional Information:")
        if "product_name" in result.additional_info:
            print(f"Product Name: {result.additional_info['product_name']}")
        if "available_sizes" in result.additional_info:
            print(f"Available Sizes: {', '.join(result.additional_info['available_sizes'])}")


if __name__ == "__main__":
    print("Checking product availability...")
    main()
