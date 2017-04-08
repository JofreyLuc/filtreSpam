from glob import glob
from math import log
import re
from copy import deepcopy
import os
import sys

#Renvoie un dictionnaire crée depuis un fichier texte
def charger_dictionnaire(dicoFilePath, minNbOfChar=3) :
    #On utilise un dictionnaire qui lie chaque mot à un tableau[2] contenant ses probas
    #d'apparaître dans un spam ou dans un ham (au début [0,0])

    dico = {}

    with open(dicoFilePath, 'r') as file :
        for word in file :
            word = ''.join(word.split())    # Enlève les éventuels whitespace
            if len(word) >= minNbOfChar:    # Si le mot est au moins de longueur minimale
                dico[word.upper()] = [0,0]  # On capitalise le mot et on le place en clef du dico

    return dico


#Renvoie un vecteur unitaire de mots correspondant à un message
def lire_message(messageFilePath, dico) :
    dicoPresence = deepcopy(dico)   # Copie le dictionnaire afin de ne pas modifier l'original

    for mot in dicoPresence : dicoPresence[mot] = False  #On met faux à la place des [0,0]

    with open(messageFilePath, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        messageWords = re.split('\W+', content) #Séparation des mots par la ponctuation + espaces
        # On parcourt les mots présents dans le mail
        for word in messageWords :
            if word.upper() in dicoPresence :
                dicoPresence[word.upper()] = True #Si le mot capitalisé est dans le dictionnaire et dans le message
                
    return dicoPresence


#Apprend un ham en modifiant les probabilités dans le dico
def apprendre_ham(dicoProbas, message, nbHam) :
    vecteurPresence = lire_message(message, dicoProbas)
    
    for mot in (present for present in vecteurPresence if vecteurPresence[present] == True) :
        #Pour chaque mot présent, on augmente la probabilité de ham
        ancienneValeur = dicoProbas[mot][1]
        ancienneValeur *= nbHam
        ancienneValeur += 1
        ancienneValeur /= nbHam
        dicoProbas[mot][1] = ancienneValeur


#Apprend un spam en modifiant les probabilités dans le dico        
def apprendre_spam(dicoProbas, message, nbSpam) :
    vecteurPresence = lire_message(message, dicoProbas)

    for mot in (present for present in vecteurPresence if vecteurPresence[present] == True) :
        #Pour chaque mot présent, on augmente la probabilité de spam
        ancienneValeur = dicoProbas[mot][0]
        ancienneValeur *= nbSpam
        ancienneValeur += 1
        ancienneValeur /= nbSpam
        dicoProbas[mot][0] = ancienneValeur


#Apprend l'ensemble des spams et hams de la base
def apprendre_base(dicoProbas, dossierSpam, dossierHam, nbSpam, nbHam) :
    spams = 0
    hams = 0

    #On apprend nbSpam spams
    for m in glob(dossierSpam + '/*.txt') :
        if spams < nbSpam :
            apprendre_spam(dicoProbas, m, nbSpam)
            spams+=1

    #On apprend nbHam hams
    for m in glob(dossierHam + '/*.txt') :
        if hams < nbHam :
            apprendre_ham(dicoProbas, m, nbHam)
            hams+=1


#Prédit la nature d'un message en renvoyant ses probas d'être un spam / ham
def predire_message(cheminMessage, nbSpam, nbHam, dicoProbas) :
    vecteurPresence = lire_message(cheminMessage, dicoProbas)

    #On estime les probas à priori
    PspamApriori = nbSpam/(nbSpam+nbHam)
    PhamApriori = nbHam/(nbSpam+nbHam)    

    Pspam = 1
    Pham = 1
    
    #On LAALALALALA
    for j in dicoProbas :
        if vecteurPresence[j] == True :
            if dicoProbas[j][0] != 0 : Pspam += log(dicoProbas[j][0])
            if dicoProbas[j][1] != 0 : Pham += log(dicoProbas[j][1])
        else :
            if dicoProbas[j][0] != 1 : Pspam += log((1-dicoProbas[j][0]))
            if dicoProbas[j][1] != 1 : Pham += log((1-dicoProbas[j][1]))

    return (Pspam * PspamApriori, Pham * PhamApriori)


def test_dossiers(spamFolder, hamFolder, nbSpam, nbHam, dicoProbas) :
    nbSpamsTest = 0
    nbHamsTest = 0
    nbErreursSpam = 0
    nbErreursHam = 0

    for nom in glob(spamFolder + '*.txt') :
        nbSpamsTest += 1
        probas = predire_message(nom, nbSpam, nbHam, dicoProbas)
        if (probas[0] >= probas[1]) :
            print('Spam ' + nom + ' identifié comme spam (à ' + str(probas[0]*100) + '%)')
        else :
            print('Spam ' + nom + ' identifié comme ham (à ' + str(probas[1]*100) + '%)')
            nbErreursSpam += 1
            
    for nom in glob(hamFolder + '*.txt') :
        nbHamsTest += 1
        probas = predire_message(nom, nbSpam, nbHam, dicoProbas)
        if (probas[1] > probas[0]) :
            print('Ham ' + nom + ' identifié comme ham (à ' + str(probas[1]*100) + '%)')
        else :
            print('Ham ' + nom + ' identifié comme spam (à ' + str(probas[0]*100) + '%)')
            nbErreursHam += 1

    if nbErreursSpam == 0 : print('0% d\'erreurs sur les spams')
    else : print(str((nbErreursSpam/nbSpamsTest)*100) + '% d\'erreurs sur les spams')

    if nbErreursHam == 0 : print('0% d\'erreurs sur les hams')
    else : print(str((nbErreursHam/nbHamsTest)*100) + '% d\'erreurs sur les hams')

    if (nbErreursSpam+nbErreursHam) == 0 : print('0% d\'erreurs sur l\'ensemble')
    else : print(str(((nbErreursSpam+nbErreursHam)/(nbSpamsTest+nbHamsTest))*100) + '% d\'erreurs sur l\'ensemble')


    
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

    print('Apprentissage...')
    apprendre_base(dictionnaire, '../baseapp/spam/', '../baseapp/ham/', nbSpam, nbHam)

    print('Tests :')
    test_dossiers(sys.argv[1], sys.argv[2], nbSpam, nbHam, dictionnaire)
    
main()
