import random

# Lista messaggi validati con riferimenti sci-fi
# Legenda riferimenti:
# - Borges: "Library of Babel"
# - Asimov: "Foundation", "Positronic neurons", "Galactic Encyclopedia"
# - Matrix (Wachowski): "Matrix", "Oracle"
# - Star Trek: "Dilithium crystals", "Warp drive"
# - Blade Runner (Philip K. Dick): "Do Androids Dream of Electric Sheep?", "Tears in rain"
# - Star Wars: "Force", "Jedi archives"
# - 2001: A Space Odyssey: "HAL 9000", "Monolith"
# - Dune: "Spice", "Kwisatz Haderach"
# - Hitchhiker's Guide: "42", "Deep Thought"
# - Neuromancer (Gibson): "Cyberspace", "Matrix" (original)
# - Doctor Who: "TARDIS", "Time Lord"

THINKING_MESSAGES = [
    # Messaggi originali (generici knowledge management)
    "Weaving connections between ideas...",
    "Mapping the cognitive territory...",
    "Intertwining threads of understanding...",
    "Exploring conceptual pathways...",
    "Crossing the bridges of meaning...",
    "Calibrating the cognitive compass...",
    "Refining knowledge crystals...",

    # Borges
    "Consulting the Library of Babel...",  # ✓ Corretto: racconto di Borges

    # Asimov
    "Activating positronic neurons...",  # ✓ Corretto: robot di Asimov
    "Consulting the Galactic Encyclopedia...",  # ✓ Corretto: Encyclopedia Galactica (Foundation)
    "Decoding the patterns of the Foundation...",  # ✓ Corretto: Fondazione di Asimov

    # Star Trek
    "Aligning dilithium crystals...",  # ✓ Corretto (era "knowledge crystals", migliorato)
    "Navigating through hyperspace...",  # ✓ Generico sci-fi, usato in Star Trek
    "Engaging the warp drive of thought...",  # NUOVO: Star Trek

    # Matrix / Cyberpunk
    "Interfacing with the Matrix...",  # ✓ Corretto: Matrix (1999)
    "Jacking into the knowledge network...",  # NUOVO: Neuromancer/Matrix
    "Following the white rabbit of insight...",  # NUOVO: Matrix

    # Blade Runner / Philip K. Dick
    "Testing if androids dream of electric sheep...",  # ✓ Corretto (migliorato da "electric android dreams")
    "Decoding tears in rain of data...",  # ✓ Corretto: monologo finale Blade Runner
    "Distinguishing memories from implants...",  # NUOVO: Blade Runner tema memorie

    # Star Wars
    "Searching the dark side of knowledge...",  # ✓ Corretto (migliorato)
    "Consulting the Jedi archives...",  # ✓ Corretto
    "Feeling disturbances in the Force...",  # NUOVO: Star Wars
    "Using the Force to sense patterns...",  # NUOVO: Star Wars

    # 2001: A Space Odyssey
    "Opening the pod bay doors of understanding...",  # NUOVO: HAL 9000
    "Approaching the Monolith of knowledge...",  # NUOVO: 2001

    # Dune
    "The Spice must flow through the data...",  # NUOVO: Dune
    "Folding space to reach conclusions...",  # NUOVO: Dune (navigatori spaziali)
    "Awakening prescient visions...",  # NUOVO: Dune (Kwisatz Haderach)

    # Hitchhiker's Guide to the Galaxy
    "Calculating the answer to life, universe, and everything...",  # NUOVO: HHGG (42)
    "Consulting Deep Thought on this matter...",  # NUOVO: HHGG
    "Don't panic, just thinking...",  # NUOVO: HHGG

    # Doctor Who
    "Reversing the polarity of the data flow...",  # NUOVO: Doctor Who (frase classica)
    "Traveling through time and relative dimensions...",  # NUOVO: TARDIS
    "Consulting the Time Lord archives...",  # NUOVO: Doctor Who

    # Neuromancer / Cyberpunk
    "Surfing the sprawl of data...",  # NUOVO: Neuromancer
    "Decrypting the gibson...",  # NUOVO: William Gibson

    # Vari / Generici sci-fi
    "Exploring parallel universes of thought...",  # Migliorato da "parallel worlds"
    "Traversing the cognitive wormhole...",  # ✓ Generico sci-fi
    "Scanning holographic memory banks...",  # ✓ Generico sci-fi
    "Synchronizing with temporal flow...",  # ✓ Generico sci-fi
    "Charting routes through conceptual space...",  # ✓ Generico sci-fi
    "Exploring the semantic dimension...",  # ✓ Generico sci-fi
]


def get_random_thinking_message():
    """Returns a random message from the list of 25 approved messages."""
    return random.choice(THINKING_MESSAGES)
