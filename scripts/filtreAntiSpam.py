#!/usr/bin/env python
"""
Réalise l'apprentissage du filtre anti-spam basé sur le classifieur naïf de Bayes
avec la base d'apprentissage contenue dans le répertoire baseapp par défaut ou avec celui passé en paramètre
et effectue des tests sur la base de test passée en paramètre
et éventuellement le nombre de spam et de ham de cette base à tester.
Si les nombres de spam et de ham à tester ne sont pas précisés, l'ensemble de la base de test sera utilisé.
"""

from glob import glob
import os
import argparse
from moduleUtils import is_positive_integer, is_valid_directory, ask_input_for_integer_between_bounds
from moduleFiltreAntiSpam import charger_dictionnaire, apprendre_base, lissage, test_dossiers

#: Le répertoire d'apprentissage par défaut
DEFAULT_REP_APPR = "../baseapp"

def main() :
    # On parse les arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("repTest", metavar="répertoireTest", type=is_valid_directory,
                        help="répertoire contenant la base de test (contenant 2 sous-répertoires spam et ham).")
    parser.add_argument("nbSpamTest", nargs='?', metavar="nbSpam", type=is_positive_integer, 
                        help="(optionnel) nombre de spam à tester parmi ceux de la base de test.")
    parser.add_argument("nbHamTest", nargs='?', metavar="nbHam", type=is_positive_integer, 
                        help="(optionnel) nombre de ham à tester parmi ceux de la base de test.")
    parser.add_argument("-a", "--apprentissage", required = False, metavar="répertoireApprentissage", dest="repAppr", type=is_valid_directory,
                        help="le répertoire contenant la base d'apprentissage (contenant 2 sous-répertoires spam et ham).\nPar défaut, c'est le dossier baseapp qui sera utilisé.", )
    args = parser.parse_args()
    
    # Base de test
    spamTestDir = os.path.join(args.repTest, 'spam')
    hamTestDir = os.path.join(args.repTest, 'ham')
    # On affiche un warning si les répertoires de ham et spam sont introuvables
    if not os.path.isdir(spamTestDir):
        print("Warning: Aucun répertoire 'spam' n'est présent dans " + str(args.repTest))
    if not os.path.isdir(hamTestDir):
        print("Warning: Aucun répertoire 'ham' n'est présent dans " + str(args.repTest))
        
    # On prend tous les spams ou hams si la quantité n'est pas précisée ou dépasse la quantité réelle (des dossiers)
    nbMaxSpamTest = len([nom for nom in glob(os.path.join(spamTestDir, '*.txt'))])
    nbMaxHamTest = len([nom for nom in glob(os.path.join(hamTestDir, '*.txt'))])
    nbSpamTest = min(i for i in [args.nbSpamTest, nbMaxSpamTest] if i is not None)
    nbHamTest = min(i for i in [args.nbHamTest, nbMaxHamTest] if i is not None)
    
    # Base d'apprentissage 
    if args.repAppr is not None:    # Rép appr précisé
        repAppr = args.repAppr
    else:                           # Non précisé
        currentDir = os.getcwd()
        repAppr = os.path.join(currentDir, DEFAULT_REP_APPR)   # Dossier par défaut dans le répertoire courant
        if not os.path.isdir(repAppr): # On vérifie que le dossier par défaut existe
            raise ValueError("Le répertoire d'apprentissage par défaut '" + DEFAULT_REP_APPR + "' est introuvable dans " + currentDir + ".\nSi vous souhaitez utiliser un autre répertoire pour l'apprentissage, utilisez l'option -a.")
        repAppr = DEFAULT_REP_APPR
        
    spamApprDir = os.path.join(repAppr, 'spam')
    hamApprDir = os.path.join(repAppr, 'ham')
    # On affiche un warning si les répertoires de ham et spam sont introuvables
    if not os.path.isdir(spamApprDir):
        print("Warning: Aucun répertoire 'spam' n'est présent dans " + str(repAppr))
    if not os.path.isdir(hamApprDir):
        print("Warning: Aucun répertoire 'ham' n'est présent dans " + str(repAppr))
        
    # On compte le nombre de spam et de ham de la base d'apprentissage
    nbMaxSpamAppr = len([nom for nom in glob(os.path.join(spamApprDir, '*.txt'))])
    nbMaxHamAppr = len([nom for nom in glob(os.path.join(hamApprDir, '*.txt'))])
    
    # On demande à l'utilisateur de préciser le nombre de spam et de ham à utiliser pour l'apprentissage
    nbSpamAppr = ask_input_for_integer_between_bounds('Spams dans la base d\'apprentissage ? (max ' + str(nbMaxSpamAppr) + ') ',
                                                      1, nbMaxSpamAppr)
                        
    nbHamAppr = ask_input_for_integer_between_bounds('Hams dans la base d\'apprentissage ? (max ' + str(nbMaxHamAppr) + ') ',
                                                     1, nbMaxHamAppr)

    # Apprentissage
    dicoProbas = charger_dictionnaire('../dictionnaire1000en.txt')
    print('Apprentissage...')
    apprendre_base(dicoProbas, spamApprDir, hamApprDir, nbSpamAppr, nbHamAppr)

    print('Lissage...')
    epsilon = 1
    lissage(dicoProbas, nbSpamAppr, nbHamAppr, epsilon)
    
    # Tests
    print('Tests :')
    test_dossiers(spamTestDir, hamTestDir, nbSpamAppr, nbHamAppr, dicoProbas, nbSpamTest, nbHamTest)
    
if __name__ == '__main__':
    main()