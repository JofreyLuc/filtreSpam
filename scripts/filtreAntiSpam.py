import numpy as np
from glob import glob
import regex as re 

def charger_dictionnaire(dicoFilePath, minNbOfChar=3) :
    dico = {}
    with open(dicoFilePath, 'r') as f :
        for word in f :
            word = ''.join(word.split())    # Enlève les éventuels whitespace
            if len(word) < minNbOfChar:     # Si le mot est de longueur minimale
                dico[word.upper()] = False  # On capitalise le mot et on le place en clef du dico
    return dico
    
def lire_message(messageFilePath, dico) :
    with open(messageFilePath, 'r') as contenu:
        content = content_file.read()
        messageWords = re.split('\W+', content)
        # On parcourt les mots présents dans le mail
        for word in messageWords :
            if word.upper() in dico :
                dico[word.upper()] = True
     return dico

def apprendre_message(dicoProbas, message, etiquette) :
    vecteurPresence = lire_message(message)
    

def apprendre_base(cheminDico, dossierSpam, dossierHam) :
    dicoProbas = charger_dictionnaire(cheminDico)
    for (m in glob(dossierSpam + '/*.txt')) : apprendre_message(dicoProbas, m, 'SPAM')
    for (m in glob(dossierHam + '/*.txt')) : apprendre_message(dicoProbas, m, 'HAM')

    
