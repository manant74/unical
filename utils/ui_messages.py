import random

# Lista messaggi validati (25 messaggi)
THINKING_MESSAGES = [
    # Messaggi originali
    "Tessendo connessioni tra le idee...",
    "Mappando il territorio cognitivo...",
    "Intrecciando fili di comprensione...",
    "Esplorando sentieri concettuali...",
    "Attraversando i ponti del significato...",
    "Calibrando la bussola cognitiva...",
    "Raffinando cristalli di conoscenza...",
    # Messaggi fantascienza
    "Consultando la Biblioteca di Babele...",
    "Navigando attraverso l'iperspazio delle idee...",
    "Interfacciandomi con Matrix e l'Oracolo...",
    "Esplorando i mondi paralleli del sapere...",
    "Decodificando i pattern della Fondazione...",
    "Sincronizzando con il flusso temporale delle informazioni...",
    "Attraversando il wormhole cognitivo...",
    "Scandagliando la memoria olografica...",
    "Attivando i neuroni positronici...",
    "Consultando l'Enciclopedia Galattica...",
    "Tracciando rotte nello spazio concettuale...",
    "Allineando i cristalli di conoscenza dilithium...",
    "Esplorando la dimensione semantica...",
    "Impiantando ricordi di conoscenza sintetica...",
    "Testando se sono sogni di androidi elettrici...",
    "Decodificando le lacrime nella pioggia dei dati...",
    "Cercando nella lato oscuro della Forza...",
    "Consultando gli archivi Jedi della conoscenza...",
]


def get_random_thinking_message():
    """Restituisce un messaggio casuale dalla lista dei 25 messaggi approvati."""
    return random.choice(THINKING_MESSAGES)
