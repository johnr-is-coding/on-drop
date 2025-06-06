import click

from on_drop.websites.thenorthface import TheNorthFaceClient


@click.command()
@click.argument("sku")
@click.argument("color")
@click.argument("size")
@click.option("--store", "-s", default="TNF", help="Store name, default is 'TNF'")
def main(store, sku, color, size):
    client = TheNorthFaceClient()
    result = client.check_stock(sku=sku, color=color, size=size)
    print(result)
        

if __name__ == "__main__":
    print("Checking product availability...")
    main()
