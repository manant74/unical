import random

# Lista messaggi validati (25 messaggi)
THINKING_MESSAGES = [
    # Messaggi originali
    "Sto tessendo connessioni tra le idee...",
    "Sto mappando il territorio cognitivo...",
    "Sto intrecciando fili di comprensione...",
    "Sto esplorando sentieri concettuali...",
    "Sto attraversando i ponti del significato...",
    "Sto calibrando la bussola cognitiva...",
    "Sto raffinando  cristalli di conoscenza...",
    # Messaggi fantascienza
    "Sto consultando la Biblioteca di Babele...",
    "Sto navigando attraverso l'iperspazio delle idee...",
    "Sto interfacciandomi con Matrix e l'Oracolo...",
    "Sto esplorando i mondi paralleli del sapere...",
    "Sto decodificando i pattern della Fondazione...",
    "Sto sincronizzando con il flusso temporale delle informazioni...",
    "Sto attraversando il wormhole cognitivo...",
    "Sto scandagliando la memoria olografica...",
    "Sto attivando i neuroni positronici...",
    "Sto consultando l'Enciclopedia Galattica...",
    "Sto tracciando rotte nello spazio concettuale...",
    "Sto allineando i cristalli di conoscenza dilithium...",
    "Sto esplorando la dimensione semantica...",
    "Sto impiantando ricordi di conoscenza sintetica...",
    "Sto testando se sono sogni di androidi elettrici...",
    "Sto decodificando le lacrime nella pioggia dei dati...",
    "Sto cercando nella lato oscuro della Forza...",
    "Sto consultando gli archivi Jedi della conoscenza...",
]


def get_random_thinking_message():
    """Restituisce un messaggio casuale dalla lista dei 25 messaggi approvati."""
    return random.choice(THINKING_MESSAGES)
