"""The asset theme — the single service that owns which set of sprites the project draws from, and every use of it.

WHAT A THEME IS. A theme groups ALL the sprites of the game under one name: a complete, coherent set covering every subject and every variant. Changing it changes which images the mock-ups mount,
which images the review pages show, and which images the game would load — and nothing else. It is not a filter, not a variant axis, and not a fallback chain: a theme is answered in full or it is
not the current theme.

THE CURRENT THEME IS CHOSEN IN THE CODE, HERE, AND NOWHERE ELSE (operator, 2026-08-07). Not in a plan, not in a page, not on a command line: one value, one place, exactly like the tile size in
tile_scale.py. Seeing a theme name written anywhere else in the project is a defect.

NAMING, AND A COLLISION WORTH KNOWING. The review pages already have "themes" — review-server/lib/themes/*.css — which dress a PAGE in colours. That notion and this one share a word and nothing
else. This module is named asset_theme, and its CSS namesake is never reached through it.

WHY gb-gen IS THE DEFAULT. It names what exists today: everything drawn so far by the image generator for GateBeast. It is the current theme because it is the only one — and giving it a name is
what makes a second one possible without moving a single existing file.
"""

# THE CURRENT THEME. Change this line to change the theme; there is no other switch, no environment variable and no argument.
CURRENT = 'gb-gen'

# The theme that owns the images produced before themes existed. Its subtree is the historical one — assets/cutout/<type>/, assets/poc/<type>/ — so declaring it costs no move and breaks no path.
# A theme added later gets its own subtree under the same roots, and only then does the path start carrying the theme's name.
LEGACY = 'gb-gen'

# What each theme is, in one sentence, for the pages and reports that show it rather than restating it.
THEMES = {
    'gb-gen': "Le premier jeu complet, dessiné par le générateur d'images pour GateBeast.",
}


def current():
    """The theme in force. Callers ask for it rather than writing its name."""
    return CURRENT


def describe(name=None):
    """What a theme is, in one sentence. Unknown themes say so instead of pretending."""
    name = name or CURRENT
    return THEMES.get(name, f"Thème « {name} » — aucune description déclarée.")


def subtree(name=None):
    """The path fragment a theme's images live under, relative to a production root.

    The legacy theme has NO fragment, on purpose: its images were produced before the notion existed and they sit directly under their type. Giving it one would mean moving every file already
    produced, and re-recording every path in the referentiel, to gain nothing — the point of naming it is precisely that a SECOND theme becomes possible without touching the first.
    """
    name = name or CURRENT

    return '' if name == LEGACY else name
