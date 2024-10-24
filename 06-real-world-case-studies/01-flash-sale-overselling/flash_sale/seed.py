"""Seed stock once, without resetting a previous exercise run."""
import os
from pathlib import Path
from .store import FlashSaleStore


def main():
    path = os.getenv("FLASH_SALE_DB", str(Path(__file__).resolve().parents[1] / "data" / "flash_sale.sqlite3"))
    store = FlashSaleStore(path)
    for item in [("SKU-HEADSET", "Wired Headset", 5, 159900),
                 ("SKU-MOUSE", "Wireless Mouse", 20, 89900)]:
        try:
            store.add_product(*item)
            print(f"Seeded: {item[0]}")
        except __import__('sqlite3').IntegrityError:
            print(f"Already exists: {item[0]} (not reset)")


if __name__ == "__main__":
    main()
