import logging

# Création d'un logger nommé "CONSUMER".
# Ce nom permettra d'identifier les logs provenant du consumer.
logger = logging.getLogger("CONSUMER")

# Définit le niveau minimum des logs que le logger va traiter.
# DEBUG est le niveau le plus détaillé.
# Les niveaux DEBUG, INFO, WARNING, ERROR et CRITICAL seront pris en compte.
logger.setLevel(logging.DEBUG)

# Création d'un handler qui permet d'envoyer les logs vers la console.
# Dans Azure DevOps, ces logs seront visibles dans les logs du pipeline.
console_handler = logging.StreamHandler()

# Définit le niveau minimum des logs affichés par ce handler.
console_handler.setLevel(logging.DEBUG)

# Définit le format des messages affichés dans la console.
#
# %(asctime)s     -> date et heure du log
# %(name)s        -> nom du logger ("CONSUMER")
# %(levelname)s   -> niveau du log (DEBUG, INFO, ERROR...)
# %(message)s     -> message que nous avons envoyé au logger
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Associe le format défini au handler de la console.
console_handler.setFormatter(formatter)

# Ajoute le handler au logger.
# Les messages envoyés avec logger.info(), logger.error(), etc.
# seront ainsi affichés dans la console.
logger.addHandler(console_handler)
