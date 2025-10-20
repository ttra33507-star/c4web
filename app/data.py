"""Static data used as placeholders until real persistence is added."""

SERVICES = [
    {
        "name": "Minimal Workspace",
        "price": 49.99,
        "image": "download (1).jpg",
        "desc": "Compact essentials kit for focused solo creators.",
    },
    {
        "name": "Ergonomic Chair",
        "price": 199.99,
        "image": "download (2).jpg",
        "desc": "Lumbar support and adaptive seating for long sessions.",
    },
    {
        "name": "Wireless Charger",
        "price": 29.99,
        "image": "download (3).jpg",
        "desc": "Qi-certified fast charging pad built for shared desks.",
    },
    {
        "name": "Noise-Canceling Headphones",
        "price": 89.99,
        "image": "download (3).jpg",
        "desc": "Immersive audio with hybrid ANC for open offices.",
    },
    {
        "name": "Smart Desk Organizer",
        "price": 59.99,
        "image": "download (3).jpg",
        "desc": "Wireless charging, pen storage, and cable routing combined.",
    },
    {
        "name": "LED Monitor Light",
        "price": 39.99,
        "image": "download (3).jpg",
        "desc": "Glare-free top lighting with dimming presets.",
    },
    {
        "name": "Portable Laptop Stand",
        "price": 24.99,
        "image": "download (3).jpg",
        "desc": "Foldable aluminium riser for ergonomic travel setups.",
    },
    {
        "name": "Digital Drawing Tablet",
        "price": 129.99,
        "image": "download (3).jpg",
        "desc": "Battery-free stylus with 8,192 levels of pressure sensitivity.",
    },
]

LICENSE_DATA: list[dict] = []
ORDER_HISTORY: list[dict] = []
TRANSACTION_HISTORY = {
    "total_amount": 0.0,
    "count": 0,
    "transactions": [],
}
