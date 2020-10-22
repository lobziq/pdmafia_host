from transliterate import translit
from typing import List, Set

mappings = {
    '0': 'o'
}


def get_variations(nickname: str) -> Set[str]:
    # дефолт ник бует в ловеркейсе - сравнивать буем только ловеркейс в дальнейшем
    nickname_lowered = nickname.lower()
    variations = {nickname_lowered}

    # ник с заменой символов типа нулей или единиц в нике для любителей 1337
    nickname_noleet = ''.join([mappings[s] if s in mappings.keys() else s for s in nickname_lowered])
    variations.add(nickname_noleet)

    # ник транслитом на русский + оригинальный
    variations.add(translit(nickname_noleet, 'ru'))

    # первая часть ника, типа baza_kaif + транслит для неё
    nickname_first_part = nickname_noleet.split('_')[0]
    variations.add(nickname_first_part)
    variations.add(translit(nickname_first_part, 'ru'))

    return variations
