import numpy as np
from glob import glob

def charger_dictionnaire() :
    1+1

def lire_message() :
    1+1

def apprendre_message(dicoProbas, message, etiquette) :
    vecteurPresence = lire_message(message)
    

def apprendre_base(cheminDico, dossierSpam, dossierHam) :
    dicoProbas = charger_dictionnaire(cheminDico)
    for (m in glob(dossierSpam + '/*.txt')) : apprendre_message(dicoProbas, m, 'SPAM')
    for (m in glob(dossierHam + '/*.txt')) : apprendre_message(dicoProbas, m, 'HAM')

    
