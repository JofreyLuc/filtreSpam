"""
Module contenant toutes les fonctions liées au filtre anti-spam.
"""

from glob import glob
from math import log, exp
import re
from copy import deepcopy
import os
import sys
import json
from os import path

# Paramètres par défaut
#: Le répertoire d'apprentissage par défaut
DEFAULT_REP_APPR = "../baseapp"
#: Le dictionnaire par défaut
DEFAULT_DICT = "../dictionnaire1000en.txt"
#: Le nombre de caractères minimum à partir duquel un mot du dictionnaire est pris en compte
DEFAULT_MIN_CHAR_DICT = 3
#: Paramètre du lissage
EPSILON = 1

# Identifieurs des différents champs pour la sauvegarde du classifieur dans un fichier json
DICO_PROBA_JSON_NAME = "DICO_PROBA"
NB_SPAM_JSON_NAME    = "NB_SPAM"
NB_HAM_JSON_NAME     = "NB_HAM"

def charger_dictionnaire(dicoFilePath, minNbOfChar=DEFAULT_MIN_CHAR_DICT) :
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


def apprendre_ham(dicoProbas, nbHam, message) :
    """
    Met à jour le classifieur en apprenant le ham.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des attributs du classifieur.
    nbHam : int
        Le nombre totale de hams que le classifieur va apprendre.
        Fait partie des attributs du classifieur.
    message : str
        Le ham appris par le classifieur.
    """
    vecteurPresence = lire_message(message, dicoProbas)
    
    for mot in (present for present in vecteurPresence if vecteurPresence[present] == True) :
        #Pour chaque mot présent, on augmente la probabilité de ham
        ancienneValeur = dicoProbas[mot][1]
        ancienneValeur *= nbHam
        ancienneValeur += 1
        ancienneValeur /= nbHam
        dicoProbas[mot][1] = ancienneValeur

        
def apprendre_spam(dicoProbas, nbSpam, message) :
    """
    Met à jour le classifieur en apprenant le spam.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des attributs du classifieur.
    nbSpam : int
        Le nombre totale de spams que le classifieur va apprendre.
        Fait partie des attributs du classifieur.
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

        
def apprendre_base(dicoProbas, dossierSpam, dossierHam, nbSpam, nbHam) :
    """
    Met à jour le classifieur en apprenant l'ensemble des spams et des hams de la base.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des attributs du classifieur.
    dossierSpam : str
        Le chemin du dossier qui contient tous les spams de la base d'apprentissage.
    dossierHam : str
        Le chemin du dossier qui contient tous les hams de la base d'apprentissage.
    nbHam : int
        Le nombre totale de spams que le classifieur va apprendre.
        Fait partie des attributs du classifieur.
    nbSpam : int
        Le nombre totale de spams que le classifieur va apprendre.
        Fait partie des attributs du classifieur.
    """
    spams = 0
    hams = 0

    #On apprend nbSpam spams
    for m in glob(dossierSpam + '/*.txt') :
        apprendre_spam(dicoProbas, nbSpam, m)
        spams+=1
        if spams >= nbSpam : break
        
    #On apprend nbHam hams
    for m in glob(dossierHam + '/*.txt') :
        apprendre_ham(dicoProbas, nbHam, m)
        hams+=1
        if hams >= nbHam : break

        
def lissage(dicoProbas, nbSpam, nbHam, epsilon) :
    """
    Réalise le lissage des probas afin d'éviter les probas nulles.
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des attributs du classifieur.
    nbSpam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    nbHam : int
        Le nombre totale de hams que le classifieur a appris.
        Fait partie des attributs du classifieur.    
    epsilon : int
        Paramètre du lissage.
    """
    for mot in dicoProbas :
        #On ajoute epsilon dans la probabilité spam
        ancienneValeurSpam = dicoProbas[mot][0]
        ancienneValeurSpam *= nbSpam
        ancienneValeurSpam = (ancienneValeurSpam + epsilon) / (nbSpam + 2*epsilon)
        dicoProbas[mot][0] = ancienneValeurSpam

        #On ajoute epsilon dans la probabilité ham
        ancienneValeurHam = dicoProbas[mot][1]
        ancienneValeurHam *= nbHam
        ancienneValeurHam = (ancienneValeurHam + epsilon) / (nbHam + 2*epsilon)
        dicoProbas[mot][1] = ancienneValeurHam

        
def predire_message(cheminMessage, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori) :
    """
    Prédit la nature du message (spam/ham) à l'aide du classifieur
    et retourne la probabilité qu'il s'agisse d'un spam et celle qu'il s'agisse d'un ham.
        
    Parameters
    ----------    
    cheminMessage : str
        Le chemin du message à analyser.
    nbHam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    nbSpam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Fait partie des attributs du classifieur.
    
    Returns
    -------
    tuple
        Un tuple de la forme (probabilité spam, probabilité ham).
    """ 
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

    return (logPspam + log(PspamApriori), logPham + log(PhamApriori))


def test_dossiers(spamFolder, hamFolder, nbSpam, nbHam, dicoProbas, nbSpamsTest, nbHamsTest) :
    """
    Teste le filtre sur une base de test.
    
    Parameters
    ----------
    spamFolder : str
        Le dossier de la base de test contenant les spams.
    hamFolder : str
        Le dossier de la base de test contenant les hams.
    nbSpam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    nbHam : int
        Le nombre totale de hams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Modifié à la sortie de la fonction.
        Fait partie des attributs du classifieur.
    nbSpamsTest : int
        Le nombre de spams à tester dans le dossier précisé.
    nbHamsTest : int
        Le nombre de hams à tester dans le dossier précisé.
    """
    nbSpamsCourant = 0
    nbHamsCourant = 0
    nbErreursSpam = 0
    nbErreursHam = 0

    PspamApriori = nbSpam/(nbSpam+nbHam)
    PhamApriori = nbHam/(nbSpam+nbHam)

    #Pour tous les spams de test
    for msgFilePath in glob(path.join(spamFolder, '*.txt')) :
        nbSpamsCourant += 1
        probas = predire_message(msgFilePath, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori)
        #On calcule la proba a posteriori
        probaspam = 1. / (1. + exp(probas[1] - probas[0]))
        
        print('Spam ' + msgFilePath + ', P(SPAM) = {0}, P(HAM) = {1}'.format(probaspam, 1-probaspam))
        
        if (probas[0] >= probas[1]) :
            print('-> identifié comme spam')
        else :
            print('-> identifié comme ham **erreur**')
            nbErreursSpam += 1
        if nbSpamsCourant >= nbSpamsTest : break

    #Pour tous les hams de test
    for msgFilePath in glob(path.join(hamFolder, '*.txt')) :
        nbHamsCourant += 1
        probas = predire_message(msgFilePath, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori)
        #On calcule la proba a posteriori
        probaspam = 1. / (1. + exp(probas[1] - probas[0]))

        print('Ham ' + msgFilePath + ', P(SPAM) = {0}, P(HAM) = {1}'.format(probaspam, 1-probaspam))
        
        if (probas[1] > probas[0]) :
            print('-> identifié comme ham')
        else :
            print('-> identifié comme spam **erreur**')
            nbErreursHam += 1
        if nbHamsCourant >= nbHamsTest : break
        
    print("\n")
    if nbErreursSpam == 0 : print('0% d\'erreurs sur les spams')
    else : print('{0:.2f}% d\'erreurs sur les spams'.format((nbErreursSpam/nbSpamsTest)*100))

    if nbErreursHam == 0 : print('0% d\'erreurs sur les hams')
    else : print('{0:.2f}% d\'erreurs sur les hams'.format((nbErreursHam/nbHamsTest)*100))

    if (nbErreursSpam+nbErreursHam) == 0 : print('0% d\'erreurs sur l\'ensemble')
    else : print('{0:.2f}% d\'erreurs sur l\'ensemble'.format(((nbErreursSpam+nbErreursHam)/(nbSpamsTest+nbHamsTest))*100))

    
def sauvegarder_filtre(cheminFichier, dicoProbas, nbSpam, nbHam):
    """
    Sauvegarde les attributs/données du filtre (c-à-d du classifieur) dans une fichier.
    
    Parameters
    ----------    
    cheminFichier : str
        Le chemin du fichier dans lequel sauvegarder le filtre.
        Si le fichier existe déjà, il sera écrasé.
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
        Fait partie des attributs du classifieur.
    nbHam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    nbSpam : int
        Le nombre totale de spams que le classifieur a appris.
        Fait partie des attributs du classifieur.
    """ 
    with open(cheminFichier, 'w') as f:
        jsonData = {}
        json.dump({NB_SPAM_JSON_NAME:nbSpam, NB_HAM_JSON_NAME:nbHam, DICO_PROBA_JSON_NAME:dicoProbas}, f)

        
def charger_filtre(cheminFichier):
    """
    Charge les attributs/données du filtre (c-à-d du classifieur) depuis un fichier.
    
    Parameters
    ----------    
    cheminFichier : str
        Le chemin du fichier dans lequel est sauvegardé le filtre.
        
    Returns
    -------
    tuple
        Les attributs du classifieur sous la forme (dicoProbas, nbSpam, nbHam)
    
    Raises
    ------
    ValueError
        Si le fichier passé en paramètre n'est pas un fichier de filtre valide.
    """
    with open(cheminFichier, 'r') as f:
        try:
            jsonData = json.load(f)
            nbSpam = jsonData[NB_SPAM_JSON_NAME]
            nbHam = jsonData[NB_HAM_JSON_NAME]
            dicoProbas = jsonData[DICO_PROBA_JSON_NAME]
        except (ValueError, KeyError) as e:
            raise ValueError("Le fichier " + cheminFichier + " n'est pas un fichier de filtre valide.")
            
    return (dicoProbas, nbSpam, nbHam)


def ajouter_mail(dicoProbas, nbSpam, nbHam, fichierMail, epsilon, isSpam) :
    """
    Ajoute un mail supplémentaire dans le dictionnaire (en ligne).
    
    Parameters
    ----------
    dicoProbas : dict
        Les probabilités sous forme de dictionnaire.
    fichierMail : str
        Le chemin du fichier dans lequel se trouve le mail.
    nbHam : int
        Le nombre total de spams que le classifieur a appris.
    nbSpam : int
        Le nombre total de spams que le classifieur a appris.
    epsilon : int
        Le epsilon utilisé dans le lissage.
    isSpam : boolean
        Le type de mail à apprendre.
    """

    vecteurPresence = lire_message(fichierMail, dicoProbas)
    
    for mot in dicoProbas :
        if isSpam :
            exNbSpam = (nbSpam + 2 * epsilon)
            nb_occu = (dicoProbas[mot][0] * exNbSpam) - epsilon
            if vecteurPresence[mot] == True : nb_occu += 1
            nb_occu += epsilon
            exNbSpam += 1
            dicoProbas[mot][0] = nb_occu / exNbSpam
        else :
            exNbHam = (nbHam + 2 * epsilon)
            nb_occu = (dicoProbas[mot][1] * exNbHam) - epsilon
            if vecteurPresence[mot] == True : nb_occu += 1
            nb_occu += epsilon
            exNbHam += 1
            dicoProbas[mot][1] = nb_occu / exNbHam
        
        
