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

def apprendre_ham(dicoProbas, message, nbHam) :
    vecteurPresence = lire_message(message)
    for (mot : vecteurPresence) :
        ancienneValeur = dicoProbas[mot][1]
        ancienneValeur *= nbHam
        ancienneValeur += 1
        ancienneValeur /= nbHam
        dicoProbas[mot][1] = ancienneValeur

def apprendre_spam(dicoProbas, message, nbSpam) :
    vecteurPresence = lire_message(message)
    for (mot : vecteurPresence) :
        ancienneValeur = dicoProbas[mot][0]
        ancienneValeur *= nbSpam
        ancienneValeur += 1
        ancienneValeur /= nbSpam
        dicoProbas[mot][0] = ancienneValeur
    
def apprendre_base(cheminDico, dossierSpam, dossierHam) :
    dicoProbas = charger_dictionnaire(cheminDico)
    for (m in glob(dossierSpam + '/*.txt')) : apprendre_message(dicoProbas, m, 'SPAM')
    for (m in glob(dossierHam + '/*.txt')) : apprendre_message(dicoProbas, m, 'HAM')

def predire_message(cheminMessage, nbSpam, nbHam, dicoProbas) :
    vecteurPresence = lire_message(cheminMessage)
    Pspam = nbSpam/(nbSpam+nbHam)
    Pham = nbHam/(nbSpam+nbHam)
    #PASSAGE EN LOG
    for (j in dicoProbas) :
        if (j in vecteurPresence) :
            Pspam *= dicoProbas[j][0]
            Pham *= dicoProbas[j][1]
        else :
            Pspam *= (1-dicoProbas[j][0])
            Pham *= (1-dicoProbas[j][1])
    
