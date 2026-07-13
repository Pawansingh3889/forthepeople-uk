"""Freedom of Information signposting.

FOI is a right, not a dataset, so there is no API to fetch. This turns "I want
to know X about my council" into a concrete route: a request link for the
selected council's governing authority on WhatDoTheyKnow, the official
guidance, and a ready-to-edit request template. The authority name comes from
the registry, so the link tracks who actually governs each place.
"""
from __future__ import annotations

from urllib.parse import quote

from registry import REGISTRY, UK_ALL

WDTK = "https://www.whatdotheyknow.com"
GOV_GUIDE = "https://www.gov.uk/make-a-freedom-of-information-request"
ICO_GUIDE = "https://ico.org.uk/for-the-public/official-information/"
RESPONSE_DAYS = 20


def foi_links(council: str) -> dict:
    """Request route and guidance links for a council's governing authority.

    For the whole-UK view (or an unknown council) the WhatDoTheyKnow link is
    the generic find-an-authority page instead of a pre-filled search.
    """
    entry = REGISTRY.get(council)
    authority = None if (not entry or council == UK_ALL) else entry.authority
    if authority:
        find = f"{WDTK}/select_authority?query={quote(authority)}"
    else:
        find = f"{WDTK}/select_authority"
    return {
        "authority": authority,
        "whatdotheyknow": find,
        "gov_guide": GOV_GUIDE,
        "ico_guide": ICO_GUIDE,
        "response_days": RESPONSE_DAYS,
    }


def request_template(authority: str | None, topic: str = "[describe the information you want]") -> str:
    """A plain FOI request the user can copy, edit, and send."""
    name = authority or "[council name]"
    return (
        f"Dear {name},\n\n"
        "Under the Freedom of Information Act 2000, please provide the following "
        "recorded information:\n\n"
        f"{topic}\n\n"
        "If any part of this request is exempt, please release the remainder and "
        "cite the exemption you are relying on for the rest. If a clarification "
        "would help you answer, please contact me.\n\n"
        "Yours faithfully,\n"
        "[your name]"
    )
