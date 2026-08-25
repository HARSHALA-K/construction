import re

def detect_intent(query, pending_intent=None):
    query = query.lower().strip()

    # Continue an unfinished calculator conversation
    if pending_intent in {"tile", "material", "project", "interior"}:
        return pending_intent

    # Material price
    if (
        any(x in query for x in ["price", "rate", "latest price", "market price"])
        and any(x in query for x in [
            "cement", "steel", "sand", "brick", "bricks",
            "aggregate", "tmt", "concrete"
        ])
    ):
        return "material_price"

    # Tile calculator
    if any(x in query for x in [
        "tile", "tiles", "tiling", "floor tile", "flooring tile"
    ]):
        return "tile"

    # Interior estimator
    if any(x in query for x in [
        "interior", "interior cost", "interior estimate",
        "modular kitchen", "furniture", "false ceiling"
    ]):
        return "interior"

    # Project estimator
    if any(x in query for x in [
        "project cost", "construction cost",
        "construction estimate", "project estimate",
        "cost per sqft", "cost per sq ft",
        "building cost", "house construction cost"
    ]):
        return "project"

    # Material / brick estimator
    if any(x in query for x in [
        "brick quantity", "material quantity",
        "material estimate", "cement quantity",
        "materials required", "how much material"
    ]):
        return "material"

    return "rag"