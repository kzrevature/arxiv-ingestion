import yaml

CATEGORIES_FILE_PATH = "src/categories.yml"


def load_categories() -> list[dict]:
    """Loads categories into memory from yaml file."""
    with open(CATEGORIES_FILE_PATH) as f:
        return yaml.load(f, yaml.Loader)


def build_category_id_reference_dict() -> dict[str, int]:
    """
    Builds a mapping from category codes to their ids.

    e.g.
     - cs.CR -> 7
     - math.GT -> 62
    """
    categories_list = load_categories()
    return {entry["code"]: entry["id"] for entry in categories_list}
