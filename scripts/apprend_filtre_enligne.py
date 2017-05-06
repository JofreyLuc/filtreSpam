#!/usr/bin/env python
"""
Modifie un classifieur existant (provenant d'un fichier json) en apprenant un spam ou un ham.
"""

import argparse
from moduleUtils import is_valid_mail_type, is_valid_file
from moduleFiltreAntiSpam import charger_filtre, ajouter_mail, sauvegarder_filtre, EPSILON

def main():
    # On parse les arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("fichierFiltre", metavar="fichierFiltre", type=is_valid_file,
                        help="fichier contenant les données du filtre à mettre à jour.")
    parser.add_argument("mail", metavar="mail", type=is_valid_file,
                        help="mail à apprendre.")
    parser.add_argument("type", metavar="type", type=is_valid_mail_type,
                        help="type du mail à apprendre : HAM ou SPAM.")
    args = parser.parse_args()

    fichierFiltre = args.fichierFiltre
    mail = args.mail
    isSpam = args.type == "SPAM"
    
    # Apprentissage en ligne
    (dicoProbas, nbSpam, nbHam) = charger_filtre(fichierFiltre)
    ajouter_mail(dicoProbas, nbSpam, nbHam, mail, EPSILON, isSpam)
    sauvegarder_filtre(fichierFiltre, dicoProbas, nbSpam, nbHam)
    
    print("Modification du filtre '" + fichierFiltre + "' par apprentissage sur le " + type + " '" + mail + "'.")

    
if __name__ == '__main__':
    main()
