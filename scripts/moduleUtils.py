"""
Module contenant quelques fonctions utilitaires.
"""

from __future__ import print_function
from argparse import ArgumentTypeError
import os
import sys

def eprint(*args, **kwargs):
    """
    Ecrit sur stderr.
    """
    print(*args, file=sys.stderr, **kwargs)

def is_valid_mail_type(type):
    """
    Vérifie que le type du mail est soit SPAM soit HAM
    (insensible à la casse).
    
    Raises
    ------
    ArgumentTypeError
        Si la valeur passé en paramètre ne correspond pas à SPAM ou HAM.
    """
    type = type.upper()
    if type != 'SPAM' and type != 'HAM':
        raise ArgumentTypeError("Type invalide : %s. SPAM ou HAM requis." % type)
    return type
    
def is_positive_integer(value):
    """
    Vérifie que la valeur passée en paramètre est bien un entier positif.
    
    Raises
    ------
    ArgumentTypeError
        Si la valeur passé en paramètre n'est pas un entier positif.
    """
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise ValueError
    except ValueError:
        raise ArgumentTypeError("%s n'est pas un entier positif." % value)
    return ivalue

def is_valid_directory(dirpath):
    """
    Vérifie si la chaîne de caractères passée en paramètre correspond bien à un répertoire existant.
    
    Raises
    ------
    ArgumentTypeError
        Si le répertoire n'existe pas ou n'est pas un répertoire.
    """
    if not os.path.isdir(dirpath):
        raise ArgumentTypeError("%s n'existe pas ou n'est pas un répertoire." % dirpath)
    return dirpath
    
def is_valid_file(filePath):
    """
    Vérifie si la chaîne de caractères passée en paramètre correspond bien à un fichier existant.
    
    Raises
    ------
    ArgumentTypeError
        Si le fichier n'existe pas ou n'est pas un fichier valide.
    """
    if not os.path.isfile(filePath):
        raise ArgumentTypeError("%s n'existe pas ou n'est pas un fichier." % filePath)
    return filePath
    
def ask_input_for_integer_between_bounds(prompt, lowerBounds, upperBounds):
    """
    Demande à l'utilisateur d'entrer un entier compris entre deux bornes en affichant le message passé en paramètre.

    Parameters
    ----------
    prompt : str
        Le message a affiché.
    lowerBounds : int
        La borne inférieur (inclusive).
    upperBounds : int
        La borne supérieur (inclusive)
        
    Returns
    -------
    int
        L'entier entré par l'utilisateur.
    """
    errorMsg = "Entrée invalide. Entier compris entre " + str(lowerBounds) + " et " + str(upperBounds) + " (inclus) requis."
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print(errorMsg)
            continue

        if value < lowerBounds or value > upperBounds:
            print(errorMsg)
            continue
        else:
            break
    return value