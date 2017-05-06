#!/usr/bin/env python
"""
Réalise l'apprentissage du filtre anti-spam basé sur le classifieur naïf de Bayes
avec la base d'apprentissage et sur le nombre de spam et de ham passés en paramètres
et sauvegarde le classifieur/filtre dans le fichier passé en argument (format json).
Si les nombres de spam et de ham ne sont pas précisés, l'ensemble de la base d'apprentissage sera utilisé.
"""

from glob import glob
import argparse
import os
from moduleUtils import is_positive_integer, is_valid_directory, is_valid_file
from moduleFiltreAntiSpam import charger_dictionnaire, apprendre_base, sauvegarder_filtre, lissage, DEFAULT_DICT, EPSILON

def main():
    # On parse les arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("fichierFiltre", metavar="fichierFiltre",
                        help="fichier de sortie où les données du filtre seront sauvegardées.")
    parser.add_argument("repAppr", metavar="répertoireApprentissage", type=is_valid_directory,
                        help="répertoire contenant la base d'apprentissage (contenant 2 sous-répertoires spam et ham).")
    parser.add_argument("nbSpam", nargs='?', metavar="nbSpam", type=is_positive_integer,
                        help="(optionnel) nombre de spam à apprendre parmi ceux de la base d'apprentissage.")
    parser.add_argument("nbHam", nargs='?', metavar="nbHam", type=is_positive_integer,
                        help="(optionnel) nombre de ham à apprendre parmi ceux de la base d'apprentissage.")
    parser.add_argument("-d", "--dictionnaire", required = False, metavar="dictionnaire", dest="dict", type=is_valid_file,
                        help="le dictionnaire contenant les mots à prendre en compte.\nPar défault, c'est le fichier '" + DEFAULT_DICT + "' qui sera utilisé.")                        
    args = parser.parse_args()

    # Dictionnaire
    if args.dict is not None:       # Dico précisé
        dict = args.dict
    else:                           # Non précisé
        currentDir = os.getcwd()
        dict = os.path.join(currentDir, DEFAULT_DICT)   # Fichier par défaut dans le répertoire courant
        if not os.path.isfile(dict): # On vérifie que le fichier par défaut existe
            raise ValueError("Le dictionnaire par défaut '" + DEFAULT_DICT + "' est introuvable dans " + currentDir + ".\nSi vous souhaitez utiliser un autre dictionnaire pour l'apprentissage, utilisez l'option -d.")
        dict = DEFAULT_DICT
    
    spamDir = os.path.join(args.repAppr, 'spam')
    hamDir = os.path.join(args.repAppr, 'ham')
    # On affiche un warning si les répertoires de ham et spam sont introuvables
    if not os.path.isdir(spamDir):
        print("Warning: Aucun répertoire 'spam' n'est présent dans " + str(args.repAppr))
    if not os.path.isdir(hamDir):
        print("Warning: Aucun répertoire 'ham' n'est présent dans " + str(args.repAppr))

    # On prend tous les spams ou hams si la quantité n'est pas précisée ou dépasse la quantité réelle (des dossiers)
    nbMaxSpam = len([nom for nom in glob(os.path.join(spamDir, '*.txt'))])
    nbMaxHam = len([nom for nom in glob(os.path.join(hamDir, '*.txt'))])
    nbSpam = min(i for i in [args.nbSpam, nbMaxSpam] if i is not None)
    nbHam = min(i for i in [args.nbHam, nbMaxHam] if i is not None)
    

    # On commence l'apprentissage
    dicoProbas = charger_dictionnaire(dict)
    print("Apprentissage sur " + str(nbSpam) + " spams et " + str(nbHam) + " hams...")
    apprendre_base(dicoProbas, spamDir, hamDir, nbSpam, nbHam)
    # On lisse
    print("Lissage...")
    lissage(dicoProbas, nbSpam, nbHam, EPSILON)
    # On sauvegarde le filtre
    sauvegarder_filtre(args.fichierFiltre, dicoProbas, nbSpam , nbHam)
    print("Classifieur enregistré dans '" + args.fichierFiltre + "'.")

if __name__ == '__main__':
    main()