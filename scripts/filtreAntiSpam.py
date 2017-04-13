from glob import glob
from math import log
import re
from copy import deepcopy
import os
import sys

def charger_dictionnaire(dicoFilePath, minNbOfChar=3) :
    """
    Charge un dictionnaire de mots depuis un fichier texte.
    
    Parameters
    ----------
    dicoFilePath : str
        Le chemin du fichier texte contenant le dictionnaire.
        Le dictionnaire doit contenir un seul mot par ligne (sans espace).
    minNbOfChar : int
        Le nombre de caractères minimal à partir duquel un mot est pris en compte.
    
    Returns
    -------
    dict
        Un dictionnaire avec chaque mot en capital comme clef et un tableau [0, 0] comme valeur.
    """

    dico = {}

    with open(dicoFilePath, 'r') as file :
        for word in file :
            word = ''.join(word.split())    # Enlève les éventuels whitespace
            if len(word) >= minNbOfChar:    # Si le mot est au moins de longueur minimale
                dico[word.upper()] = [0,0]  # On capitalise le mot et on le place en clef du dico

    return dico

def lire_message(messageFilePath, dico) :
    """
    Lit un message et le traduit en une représentation sous forme de vecteur binaire x à partir d’un dictionnaire.
    
    Parameters
    ----------
    messageFilePath : str
        Le chemin du fichier texte contenant le message/mail à lire.
    dico : dict
        Le dictionnaire de mots dont la présence est vérifiée.
    
    Returns
    -------
    dict
        Un dictionnaire représentant le vecteur binaire (mot -> booléen).
    """
    dicoPresence = deepcopy(dico)   # Copie le dictionnaire afin de ne pas modifier l'original

    for mot in dicoPresence : dicoPresence[mot] = False  # On met faux à la place des [0,0]

    with open(messageFilePath, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        messageWords = re.split('\W+', content) # Séparation des mots par la ponctuation + espaces
        # On parcourt les mots présents dans le mail
        for word in messageWords :
            if word.upper() in dicoPresence :
                dicoPresence[word.upper()] = True # Si le mot capitalisé est dans le dictionnaire et dans le message
                
    return dicoPresence


#Apprend un ham en modifiant les probabilités dans le dico
def apprendre_ham(dicoProbas, nbHam, message) :
    """
    Met à jour le classifieur en apprenant le ham.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des paramètres du classifieur.
    nbHam : int
        Le nombre totale de hams que le classifieur va apprendre.
        Fait partie des paramètres du classifieur.
    message : str
        Le hame appris par le classifieur.
    """
    vecteurPresence = lire_message(message, dicoProbas)
    
    for mot in (present for present in vecteurPresence if vecteurPresence[present] == True) :
        #Pour chaque mot présent, on augmente la probabilité de ham
        ancienneValeur = dicoProbas[mot][1]
        ancienneValeur *= nbHam
        ancienneValeur += 1
        ancienneValeur /= nbHam
        dicoProbas[mot][1] = ancienneValeur


#Apprend un spam en modifiant les probabilités dans le dico        
def apprendre_spam(dicoProbas, nbSpam, message) :
    """
    Met à jour le classifieur en apprenant le spam.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des paramètres du classifieur.
    nbHam : int
        Le nombre totale de spams que le classifieur va apprendre.
        Fait partie des paramètres du classifieur.
    message : str
        Le spam appris par le classifieur.
    """
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
        apprendre_spam(dicoProbas, m, nbSpam)
        spams+=1
        if spams >= nbSpam : break
        
    #On apprend nbHam hams
    for m in glob(dossierHam + '/*.txt') :
        apprendre_ham(dicoProbas, m, nbHam)
        hams+=1
        if hams >= nbHam : break

        
def lissage(dicoProbas, nbSpam, nbHam, epsilon) :
    for mot in dicoProbas :
        ancienneValeurSpam = dicoProbas[mot][0]
        ancienneValeurSpam *= nbSpam
        ancienneValeurSpam = (ancienneValeurSpam + epsilon) / (nbSpam + 2*epsilon)
        dicoProbas[mot][0] = ancienneValeurSpam

        ancienneValeurHam = dicoProbas[mot][1]
        ancienneValeurHam *= nbHam
        ancienneValeurHam = (ancienneValeurHam + epsilon) / (nbHam + 2*epsilon)
        dicoProbas[mot][1] = ancienneValeurHam
        
#Prédit la nature d'un message en renvoyant ses probas d'être un spam / ham
def predire_message(cheminMessage, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori) :
    vecteurPresence = lire_message(cheminMessage, dicoProbas)

    logPspam = 0
    logPham = 0
    
    #On définit la somme des log des probas des mots
    for j in dicoProbas :
        if vecteurPresence[j] == True :
            logPspam += log(dicoProbas[j][0])
            logPham += log(dicoProbas[j][1])
        else :
            logPspam += log((1-dicoProbas[j][0]))
            logPham += log((1-dicoProbas[j][1]))

    return (logPspam * PspamApriori, logPham * PhamApriori)


def test_dossiers(spamFolder, hamFolder, nbSpam, nbHam, dicoProbas, nbSpamsTest, nbHamsTest) :
    nbSpamsCourant = 0
    nbHamsCourant = 0
    nbErreursSpam = 0
    nbErreursHam = 0

    PspamApriori = nbSpam/(nbSpam+nbHam)
    PhamApriori = nbHam/(nbSpam+nbHam)

    for nom in glob(spamFolder + '*.txt') :
        nbSpamsCourant += 1
        #PAS OUF, PROBLEMES DE PROBAS
        probas = predire_message(nom, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori)
        probaspam = abs(probas[0]/(probas[0]+probas[1]))/(nbSpam/(nbSpam+nbHam))

        print('Spam ' + nom + ', P(SPAM) = {0:.2f}, P(HAM) = {1:.2f}'.format(probaspam, 1-probaspam))

        if (probas[0] >= probas[1]) :
            print('-> identifié comme spam')
        else :
            print('-> identifié comme ham **erreur**')
            nbErreursSpam += 1
        if nbSpamsCourant >= nbSpamsTest : break
            
    for nom in glob(hamFolder + '*.txt') :
        nbHamsCourant += 1
        probas = predire_message(nom, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori)
        probaham = abs(probas[1]/(probas[0]+probas[1]))/(nbHam/(nbSpam+nbHam))

        print('Ham ' + nom + ', P(SPAM) = {0:.2f}, P(HAM) = {1:.2f}'.format(1-probaham, probaham))

        if (probas[1] > probas[0]) :
            print('-> identifié comme ham')
        else :
            print('-> identifié comme spam **erreur**')
            nbErreursHam += 1
        if nbHamsCourant >= nbHamsTest : break
        

    if nbErreursSpam == 0 : print('0% d\'erreurs sur les spams')
    else : print('{0:.2f}% d\'erreurs sur les spams'.format((nbErreursSpam/nbSpamsTest)*100))

    if nbErreursHam == 0 : print('0% d\'erreurs sur les hams')
    else : print('{0:.2f}% d\'erreurs sur les hams'.format((nbErreursHam/nbHamsTest)*100))

    if (nbErreursSpam+nbErreursHam) == 0 : print('0% d\'erreurs sur l\'ensemble')
    else : print('{0:.2f}% d\'erreurs sur l\'ensemble'.format(((nbErreursSpam+nbErreursHam)/(nbSpamsTest+nbHamsTest))*100))

  
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

    print('Lissage...')
    epsilon = 1
    lissage(dictionnaire, nbSpam, nbHam, epsilon)
    
    print('Tests :')
    test_dossiers(sys.argv[1], sys.argv[2], nbSpam, nbHam, dictionnaire,100,100)
    
main()
