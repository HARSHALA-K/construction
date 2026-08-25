import requests
from backend.config import APIFY_TOKEN

BASE_URL = (
    "https://api.apify.com/v2/actors/mai_amm~india-construction-material-prices/runs/last/dataset/items"
)


def get_material_price(
        material_name,
        city="None"
):
    response = requests.get(
        BASE_URL,
        params={
            "token": APIFY_TOKEN
        }
    )

    data = response.json()

    matches = []

    
    for item in data:

        material_match = (
            material_name.lower() in item.get(
                "material",
                ""
            ).lower()
            or
            material_name == (item.get("material") or "").lower()
        )

        city_match = (
            city is None or
            city.lower() == item.get(
                "city",
                ""
            ).lower()
        )

        if material_match and city_match:
            matches.append(
                {
                    "material": item["material"],
                    "price": item["price"],
                    "unit": item["unit"],
                    "city": item["city"],
                    "currency": item["currency"]
                }
            )

    return matches[:5]