from glob import glob
from math import log
import re
from copy import deepcopy
import os

def charger_dictionnaire(dicoFilePath, minNbOfChar=3) :
    dico = {}
    with open(dicoFilePath, 'r') as file :
        for word in file :
            word = ''.join(word.split())    # Enlève les éventuels whitespace
            if len(word) >= minNbOfChar:    # Si le mot est de longueur minimale
                dico[word.upper()] = [0,0]  # On capitalise le mot et on le place en clef du dico
    return dico
    
def lire_message(messageFilePath, dico) :
    dicoPresence = deepcopy(dico)   # Copie le dictionnaire afin de ne pas modifier l'original
    for mot in dicoPresence : dicoPresence[mot] = False
    with open(messageFilePath, 'r',encoding='utf-8', errors='ignore') as file:
        content = file.read()
        messageWords = re.split('\W+', content)
        # On parcourt les mots présents dans le mail
        for word in messageWords :
            if word.upper() in dicoPresence :
                dicoPresence[word.upper()] = True
    return dicoPresence

def apprendre_ham(dicoProbas, message, nbHam) :
    vecteurPresence = lire_message(message, dicoProbas)
    for mot in vecteurPresence :
        ancienneValeur = dicoProbas[mot][1]
        ancienneValeur *= nbHam
        ancienneValeur += 1
        ancienneValeur /= nbHam
        dicoProbas[mot][1] = int(ancienneValeur)

def apprendre_spam(dicoProbas, message, nbSpam) :
    vecteurPresence = lire_message(message, dicoProbas)
    for mot in vecteurPresence :
        ancienneValeur = dicoProbas[mot][0]
        ancienneValeur *= nbSpam
        ancienneValeur += 1
        ancienneValeur /= nbSpam
        dicoProbas[mot][0] = int(ancienneValeur)
    
def apprendre_base(cheminDico, dossierSpam, dossierHam, nbSpam, nbHam) :
    dicoProbas = charger_dictionnaire(cheminDico)
    spams = 0
    hams = 0
    for m in glob(dossierSpam + '/*.txt') :
        if spams < nbSpam :
            apprendre_spam(dicoProbas, m, nbSpam)
            spams+=1
    for m in glob(dossierHam + '/*.txt') :
        if hams < nbHam :
            apprendre_ham(dicoProbas, m, nbHam)
            hams+=1

def predire_message(cheminMessage, nbSpam, nbHam, dicoProbas) :
    vecteurPresence = lire_message(cheminMessage)
    Pspam = nbSpam/(nbSpam+nbHam)
    Pham = nbHam/(nbSpam+nbHam)
    for j in dicoProbas :
        if j in vecteurPresence :
            Pspam *= log(dicoProbas[j][0])
            Pham *= log(dicoProbas[j][1])
        else :
            Pspam *= log((1-dicoProbas[j][0]))
            Pham *= log((1-dicoProbas[j][1]))
    
def main() :
    nbMaxSpam = len([nom for nom in glob('../baseapp/spam/*.txt')])
    nbMaxHam = len([nom for nom in glob('../baseapp/ham/*.txt')])
    dictionnaire = charger_dictionnaire('../dictionnaire1000en.txt')

    nbSpam = nbMaxSpam + 1
    while nbSpam > nbMaxSpam :
        nbSpam = int(input('Spams dans la base d\'apprentissage ? (max ' + str(nbMaxSpam) + ') '))

    nbHam = nbMaxHam + 1
    while nbHam > nbMaxHam :
        nbHam = int(input('Hams dans la base d\'apprentissage ? (max ' + str(nbMaxHam) + ') '))
        
    apprendre_base('../dictionnaire1000en.txt', '../baseapp/spam/', '../baseapp/ham/', nbSpam, nbHam)

    
main()
