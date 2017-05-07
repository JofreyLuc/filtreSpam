#!/usr/bin/env python
"""
Prédit si un mail est un spam ou un ham à partir d'un filtre/classifieur
stocké dans un fichier (json) passé en argument.
"""

import argparse
from moduleUtils import is_valid_file, eprint
from moduleFiltreAntiSpam import charger_filtre, predire_message
from math import exp

def main() :
    # On parse les arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("fichierFiltre", metavar="fichierFiltre", type=is_valid_file,
                        help="fichier contenant les données du filtre.")
    parser.add_argument("mail", metavar="mail", type=is_valid_file,
                        help="mail à tester.")
    args = parser.parse_args()

    fichierFiltre = args.fichierFiltre
    mail = args.mail
    
    # On charge le fichier de filtre
    try:    
        (dicoProbas, nbSpam, nbHam) = charger_filtre(fichierFiltre)
    except ValueError as e: # N'est pas un fichier de filtre
        eprint(str(e))
        exit(-1)
    
    # Et on prédit l'étiquette du mail
    PspamApriori = nbSpam / (nbSpam + nbHam)
    PhamApriori = nbHam / (nbSpam + nbHam)
    (probaSpam, probaHam) = predire_message(mail, nbSpam, nbHam, dicoProbas, PspamApriori, PhamApriori)
    
    msg = "D'après '" + fichierFiltre + "', le message '" + mail + "' est un "
    if probaSpam > probaHam:
        msg += "SPAM à {0} !".format(1. / (1. + exp(probaHam - probaSpam)))
    else:
        msg += "HAM à {0} !".format(1. / (1. + exp(probaSpam - probaHam)))
    print(msg)
    
if __name__ == '__main__':
    main()
