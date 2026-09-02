"""Base schema — memastikan semua response API memakai field `camelCase`.

Pydantic v2: `alias_generator=to_camel` membuat field internal `snake_case`
ter-serialize sebagai `camelCase`; `populate_by_name` membuat deserialisasi
menerima keduanya (`AGENTS.md` §5).

Semua schema request/response mewarisi `CamelModel` agar konsistensi tidak
bergantung pada disiplin manual per file.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base model dengan serialisasi `camelCase` otomatis."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        str_strip_whitespace=True,
    )
