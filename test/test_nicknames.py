import pytest
from prodota.nicknames import get_variations

expected_output = {
    'Fint': {'fint', 'финт'},
    'R0ss0ha': {'r0ss0ha', 'rossoha', 'россоха'},
    # сложный кейс, над подумать как резолвить й
    'Baza_KAiF': {'baza_kaif', 'база_каиф', 'baza', 'база'}
}


@pytest.mark.parametrize('nickname, variations', [(k, v) for k, v in expected_output.items()])
def test_nicknames(nickname, variations):
    assert get_variations(nickname) == variations
