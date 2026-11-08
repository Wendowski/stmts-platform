"""Trusted server-side attachment interface. No URLs or fetching are accepted."""
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Attachment:
    attachment_id: str
    eligible: bool
    kind: str
    state: str
    alt: str = ''
    decorative: bool = False
    caption: str = ''

class AttachmentResolver(Protocol):
    def __call__(self, attachment_id: str) -> Attachment | None: ...
