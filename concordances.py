#### took box ###
import glob
import re
import os
import xml.etree.ElementTree as xml
import spacy
from spacy.cli import download
from spacy import displacy
from spacy.lang.fr import French
import fr_core_news_lg
nlp = spacy.load('fr_core_news_lg')
from spacy import tokens
from spacy.tokens import Doc
import numpy as np
import pandas as pd
from colorama import Fore, Style
import colorama
from spacy.matcher import PhraseMatcher


files = glob.glob("*.txt")
my_files = glob.glob("rejet_corp/*.txt")

def concordance_ADVERBESREST():
    data = []  # Créer une liste pour stocker les résultats de tous les fichiers

    # Création du PhraseMatcher pour les mots "seul", "seulement", "uniquement"
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
    ADVERBESREST = ["seul", "seulement", "uniquement"]
    patterns = [nlp(text) for text in ADVERBESREST]
    phrase_matcher.add('ADVERBESREST', None, *patterns)

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text

                # Recherche des occurrences des mots "seul", "seulement", "uniquement"
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["ADVERBESREST"]:
                        # Capturer le contexte gauche et droit
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        # Ajouter les données à la liste
                        data.append([context_gauche, occurrence, context_droit])

                regex_pattern = r"(?i)(ne|n\'[a-z]*)(?:\s\w+){1,3}\s(que|qu\'[a-z]*)"
                matchs = re.findall(regex_pattern, sentences)
                for match in matchs:
                    span_text = " ".join(match)
                    
                    data.append(["", span_text, ""])


    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)

    df.to_csv("ADV_REST3.csv", index=False)

concordance_ADVERBESREST()

def concordance_VERBESFACTIFS():
    data = []  

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            nlp.max_length = 10000000
            phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
            VERBESFACTIFS = ["avoir raison", "savoir", "apprendre", "comprendre", "remarquer", "étonner", "calculer", "sentir", "reconnaître", "ignorer", "découvrir", "avouer"]
            patterns = [nlp(text) for text in VERBESFACTIFS]
            phrase_matcher.add('VERBESFACTIFS', None, *patterns)
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["VERBESFACTIFS"]:
                        # Capturer le contexte gauche et droit
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        # Ajouter les données à la liste
                        data.append([context_gauche, occurrence, context_droit])

  
    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)

    # Écrire le fichier CSV
    df.to_csv("VRB_FACT.csv", index=False)

concordance_VERBESFACTIFS()

def concordance_SUBORDTEMP():
    
    data = []  

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            nlp.max_length = 10000000
            phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
            SUBORDTEMP = ["après", "avant", "tandis que", "quand", "lorsque", "fois", "pendant","à mesure que", "au moment où", "jour", "depuis que", "dès que"]
            patterns = [nlp(text) for text in SUBORDTEMP]
            phrase_matcher.add('SUBORDTEMP', None, *patterns)
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["SUBORDTEMP"]:
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        data.append([context_gauche, occurrence, context_droit])

    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)
    df.to_csv("SUB_TEMP.csv", index=False)

concordance_SUBORDTEMP()




def concordance_SUBORDOCAUSALES():
   
    data = []  # Créer une liste pour stocker les résultats de tous les fichiers

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            nlp.max_length = 10000000
            phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
            SUBORDOCAUSALES = ["puisque", "si", "quoique", "de sorte que", "bien que", "pour", "quelque", "quoi que"]
            patterns = [nlp(text) for text in SUBORDOCAUSALES]
            phrase_matcher.add('SUBORDOCAUSALES', None, *patterns)
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["SUBORDOCAUSALES"]:
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        data.append([context_gauche, occurrence, context_droit])

    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)
    df.to_csv("SUB_CAUS.csv", index=False)
concordance_SUBORDOCAUSALES()


def concordance_ADVERBESADDI():
    
    data = []  # Créer une liste pour stocker les résultats de tous les fichiers

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            nlp.max_length = 10000000
            phrase_matcher = PhraseMatcher(nlp.vocab)
            ADVERBESADDI = ["également", "aussi", "autre", "à leur tour", "nouveau"]
            patterns = [nlp(text) for text in ADVERBESADDI]
            phrase_matcher.add('ADVERBESADDI', None, *patterns)
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["ADVERBESADDI"]:
                        # Capturer le contexte gauche et droit
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        # Ajouter les données à la liste
                        data.append([context_gauche, occurrence, context_droit])

    # Créer le DataFrame avec les nouvelles colonnes
    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)

    # Écrire le fichier CSV
    df.to_csv("ADV_ADDI.csv", index=False)

concordance_ADVERBESADDI()




def concordance_PREDICATSASPECTUELS():
    data = []  # Créer une liste pour stocker les résultats de tous les fichiers

    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
            nlp.max_length = 10000000
            phrase_matcher = PhraseMatcher(nlp.vocab)
            PREDICATSASPECT = ["encore", "plus", "terminer", "déjà", "commencer", "pas encore", "demeurer", "arrêter", "toujours", "de nouveau", "cesser", "prolonger", "rester"]
            patterns = [nlp(text) for text in PREDICATSASPECT]
            phrase_matcher.add('PREDICATSASPECT', None, *patterns)
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sentences = sent.text
                matches = phrase_matcher(nlp(sentences))
                for match_id, start, end in matches:
                    if nlp.vocab.strings[match_id] in ["PREDICATSASPECT"]:
                        # Capturer le contexte gauche et droit
                        tokens = nlp(sentences)
                        context_gauche = " ".join(tokens[i].text for i in range(start))
                        occurrence = sent[start:end].text.strip()
                        context_droit = " ".join(tokens[i].text for i in range(end, len(tokens)))
                        # Ajouter les données à la liste
                        data.append([context_gauche, occurrence, context_droit])

    # Créer le DataFrame avec les nouvelles colonnes
    df = pd.DataFrame(data, columns=['Contexte Gauche', 'Occurrence_declencheur', 'Contexte Droit'])
    df.drop_duplicates(keep='first', inplace=True)

    # Écrire le fichier CSV
    df.to_csv("PRED_ASP.csv", index=False)

concordance_PREDICATSASPECTUELS()
