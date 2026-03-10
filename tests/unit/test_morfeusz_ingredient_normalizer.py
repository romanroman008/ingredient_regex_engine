from unittest.mock import create_autospec

import pytest

from regex_engine.src.regex_engine.ports.morfeusz import Morfeusz


@pytest.fixture
def morfeusz() -> Morfeusz:
    return create_autospec(Morfeusz, instance=True, spec_set=True)




