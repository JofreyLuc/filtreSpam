from glob import glob
from math import log

def charger_dictionnaire() :
    1+1

def lire_message() :
    1+1

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
            Pspam *= log(dicoProbas[j][0])
            Pham *= log(dicoProbas[j][1])
        else :
            Pspam *= log((1-dicoProbas[j][0]))
            Pham *= log((1-dicoProbas[j][1]))
    
