import re


# ============================================================
# MATERIAL CALCULATIONS
# ============================================================

def calculate_bricks(
    length: float,
    width: float,
    thickness: float,
) -> int:
    """
    Calculate estimated number of bricks from wall dimensions.

    Assumption:
        500 modular bricks per m³ of finished brickwork.

    NOTE:
        This retains the existing project behaviour.
    """

    volume = length * width * thickness
    bricks = volume * 500

    return round(bricks)


def calculate_material(
    length: float,
    width: float,
    thickness: float,
    material_type: str,
    calculation_type: str
):
    """
    Calculate construction material requirement.

    Supported materials:

        brick
        cement
        sand
        aggregate

    Brick:
        Uses the existing project assumption of
        500 bricks per m³.

    Cement / Sand / Aggregate:
        Uses preliminary M15 concrete estimation
        with nominal mix ratio:

            1 : 2 : 4
            cement : sand : aggregate

        Dry volume factor = 1.54

    Steel is intentionally not calculated here because
    reinforcement quantity cannot be reliably determined
    from only length, width and thickness.

    calculation_type:
        - brickwork: for masonry/wall brick calculations
        - concrete: for concrete material calculations

    """

    calculation_type = calculation_type.lower().strip()
    material_type = material_type.lower().strip()

    if calculation_type not in {"brickwork", "concrete"}:
            raise ValueError(
                "calculation_type must be either 'brickwork' or 'concrete'"
            )

    if material_type not in {"brick", "cement", "sand", "aggregate"}:
        raise ValueError(
            "material_type must be one of: brick, cement, sand, aggregate"
        )
    # --------------------------------------------------------
    # BASIC VOLUME
    # --------------------------------------------------------

    volume = length * width * thickness

    # --------------------------------------------------------
    # BRICK
    # --------------------------------------------------------

    if material_type in {"brick", "bricks"}:

        bricks = round(volume * 500)

        return {
            "material": "brick",
            "volume": round(volume, 3),
            "quantity": bricks,
            "unit": "bricks",
            "basis": "500 modular bricks per m³"
        }

    # --------------------------------------------------------
    # CEMENT / SAND / AGGREGATE
    # --------------------------------------------------------
    #
    # Preliminary concrete estimation:
    #
    # M15 nominal mix = 1 : 2 : 4
    #
    # Dry volume = wet volume × 1.54
    #
    # Total parts = 1 + 2 + 4 = 7
    #
    # --------------------------------------------------------

    if material_type in {
        "cement",
        "sand",
        "aggregate"
    }:

        dry_volume = volume * 1.54

        total_parts = 1 + 2 + 4

        cement_volume = (
            dry_volume * 1 / total_parts
        )

        sand_volume = (
            dry_volume * 2 / total_parts
        )

        aggregate_volume = (
            dry_volume * 4 / total_parts
        )

        # 1 cement bag = approximately 0.035 m³
        # for preliminary volume-based estimation.
        cement_bags = cement_volume / 0.035

        if material_type == "cement":

            return {
                "material": "cement",
                "concrete_volume": round(volume, 3),
                "dry_material_volume": round(
                    dry_volume,
                    3
                ),
                "quantity": round(
                    cement_bags,
                    2
                ),
                "unit": "50 kg bags",
                "mix_ratio": "1:2:4",
                "basis": "M15 preliminary nominal mix"
            }

        if material_type == "sand":

            return {
                "material": "sand",
                "concrete_volume": round(volume, 3),
                "dry_material_volume": round(
                    dry_volume,
                    3
                ),
                "quantity": round(
                    sand_volume,
                    3
                ),
                "unit": "m³",
                "mix_ratio": "1:2:4",
                "basis": "M15 preliminary nominal mix"
            }

        if material_type == "aggregate":

            return {
                "material": "aggregate",
                "concrete_volume": round(volume, 3),
                "dry_material_volume": round(
                    dry_volume,
                    3
                ),
                "quantity": round(
                    aggregate_volume,
                    3
                ),
                "unit": "m³",
                "mix_ratio": "1:2:4",
                "basis": "M15 preliminary nominal mix"
            }

    # --------------------------------------------------------
    # STEEL
    # --------------------------------------------------------

    if material_type in {"steel", "rebar", "reinforcement"}:

        raise ValueError(
            "Steel quantity cannot be estimated reliably "
            "from length, width and thickness alone. "
            "Structural reinforcement details are required."
        )

    # --------------------------------------------------------
    # UNKNOWN MATERIAL
    # --------------------------------------------------------

    raise ValueError(
        f"Unsupported material type: {material_type}"
    )


# ============================================================
# INPUT EXTRACTION
# ============================================================

def extract_material_inputs(prompt: str):

    prompt = prompt.lower()

    result = {
        "length": None,
        "width": None,
        "thickness": None,
        "material_type": None,
        "calculation_type": None
    }

    # --------------------------------------------------------
    # MATERIAL TYPE
    # --------------------------------------------------------

    material_match = re.search(
        r"\b("
        r"bricks?"
        r"|cement"
        r"|sand"
        r"|aggregate"
        r"|steel"
        r"|rebar"
        r"|reinforcement"
        r")\b",
        prompt
    )

    if material_match:

        material = material_match.group(1)

        if material in {"brick", "bricks"}:

            result["material_type"] = "brick"

        elif material in {
            "rebar",
            "reinforcement"
        }:

            result["material_type"] = "steel"

        else:

            result["material_type"] = material

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    size_match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:x|\*|×)\s*"
        r"(\d+(?:\.\d+)?)",
        prompt
    )

    if size_match:

        result["length"] = float(
            size_match.group(1)
        )

        result["width"] = float(
            size_match.group(2)
        )

    # --------------------------------------------------------
    # THICKNESS
    # --------------------------------------------------------

    thickness_match = re.search(
        r"thickness\s*(?:is\s*)?"
        r"(\d+(?:\.\d+)?)",
        prompt
    )

    if thickness_match:

        result["thickness"] = float(
            thickness_match.group(1)
        )

    # --------------------------------------------------------
    # DEFAULT MATERIAL
    # --------------------------------------------------------

    if result["material_type"] is None:

        result["material_type"] = "brick"

    if result["material_type"] in {"cement", "sand", "aggregate"}:

        result["calculation_type"] = "concrete"

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    required_fields = [
        "length",
        "width",
        "thickness"
    ]

    missing = [
        field
        for field in required_fields
        if result[field] is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result