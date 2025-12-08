from datetime import datetime


class Article:
    # later consider: abs_link, pdf_link, cat, subcat
    def __init__(
        self,
        id_: str,
        title: str,
        created_at: datetime,
        updated_at: datetime,
        categories: list[str] = [],
        abstract: str = "",
    ):
        self.id = id_
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.categories = categories
        self.abstract = abstract
