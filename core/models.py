from dataclasses import dataclass, field

from core.masking import mask_identifier


@dataclass(frozen=True)
class LoginCase:
    case_id: str
    title: str
    group: str
    kind: str
    identifier: str = field(repr=False)
    password: str = field(repr=False)
    expected: str
    error: str = ""

    @property
    def is_positive(self) -> bool:
        return self.expected == "success"

    @property
    def safe_identifier(self) -> str:
        return mask_identifier(self.identifier)

    @property
    def safe_password(self) -> str:
        return "<пусто>" if not self.password else "***"

    def __repr__(self) -> str:
        return f"{self.case_id}"

    __str__ = __repr__


@dataclass(frozen=True)
class Product:
    search_query: str
    title: str
    price: int
    color: str
    quantity: int
    url_part: str


@dataclass(frozen=True)
class Customer:
    full_name: str = field(repr=False)
    email: str = field(repr=False)
    phone: str = field(repr=False)
    address: str = field(repr=False)
    payment: str


@dataclass(frozen=True)
class OrderScenario:
    case_id: str
    title: str
    product: Product
    customer: Customer

    def __repr__(self) -> str:
        return self.case_id

    __str__ = __repr__
