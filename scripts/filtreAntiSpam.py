from glob import glob
from math import log
import re
from copy import deepcopy

def charger_dictionnaire(dicoFilePath, minNbOfChar=3) :
    dico = {}
    with open(dicoFilePath, 'r') as file :
        for word in file :
            word = ''.join(word.split())    # Enlève les éventuels whitespace
            if len(word) >= minNbOfChar:    # Si le mot est de longueur minimale
                dico[word.upper()] = False  # On capitalise le mot et on le place en clef du dico
    return dico
    
def lire_message(messageFilePath, dico) :
    dicoPresence = deepcopy(dico)   # Copie le dictionnaire afin de ne pas modifier l'original
    with open(messageFilePath, 'r') as file:
        content = file.read()
        messageWords = re.split('\W+', content)
        # On parcourt les mots présents dans le mail
        for word in messageWords :
            if word.upper() in dicoPresence :
                dicoPresence[word.upper()] = True
    return dicoPresence

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
    for (j in dicoProbas) :
        if (j in vecteurPresence) :
            Pspam *= log(dicoProbas[j][0])
            Pham *= log(dicoProbas[j][1])
        else :
            Pspam *= log((1-dicoProbas[j][0]))
            Pham *= log((1-dicoProbas[j][1]))
    
