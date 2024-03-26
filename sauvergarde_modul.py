### CODE PRINCIPAL ###
import glob
import re
import os
import xml.etree.ElementTree as xml
import spacy
from spacy.cli import download
from spacy import displacy
from spacy.lang.fr import French
import fr_core_news_lg
import string
from spacy.tokens import Token
from spacy.tokens import Doc
import numpy as np
import pandas as pd
from spacy.matcher import PhraseMatcher
import itertools
import random
import unicodedata
from collections import OrderedDict
import io
from tqdm import tqdm


def normalize_files(folder_path):
    # Parcours des sous-dossiers de cassation et rejet
    for root, dirs, _ in os.walk(folder_path):
        # Ignorer les dossiers cassation et rejet eux-mêmes
        if root.endswith(('cassation', 'rejet')):
            continue
        for filename in os.listdir(root):
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                print("Traitement du fichier :", file_path)  # Ajout d'un message d'impression
                with open(file_path, "r", encoding="utf8") as f:
                    document = f.read()

                # Appliquer toutes les normalisations aux textes bruts, sauf remove_page_numbers
                document_brut = remove_pourvoi(document)
                print("Après remove_pourvoi :", document_brut)  # Ajout d'un message d'impression
                document_brut = remove_underscores(document_brut)
                print("Après remove_underscores :", document_brut)  # Ajout d'un message d'impression
                document_brut = replace_acronyms(document_brut)
                print("Après replace_acronyms :", document_brut)  # Ajout d'un message d'impression
                document_brut = normalize_moyens(document_brut)
                print("Après normalize_moyens :", document_brut)  # Ajout d'un message d'impression
                document_brut = remove_form_feed(document_brut)
                print("Après remove_form_feed :", document_brut)  # Ajout d'un message d'impression
                document_brut = remove_extra_spaces(document_brut)
                print("Après remove_extra_spaces :", document_brut)  # Ajout d'un message d'impression
                document_brut = replace_specific_words(document_brut)
                print("Après replace_specific_words :", document_brut)  # Ajout d'un message d'impression

                # Écrire le texte nettoyé dans un nouveau fichier pour les textes bruts
                output_folder_brute = os.path.join(os.path.dirname(file_path), 'brute_texte')
                if not os.path.exists(output_folder_brute):
                    os.makedirs(output_folder_brute)
                output_file_path_brute = os.path.join(output_folder_brute, os.path.basename(file_path))
                with open(output_file_path_brute, 'w', encoding="utf8") as final_doc_brute:
                    final_doc_brute.write(document_brut)

                # Appliquer toutes les normalisations, y compris remove_page_numbers, aux textes nettoyés
                document_cleaned = remove_pourvoi(document)
                document_cleaned = remove_underscores(document_cleaned)
                document_cleaned = replace_acronyms(document_cleaned)
                document_cleaned = normalize_moyens(document_cleaned)
                document_cleaned = remove_form_feed(document_cleaned)
                document_cleaned = remove_extra_spaces(document_cleaned)
                document_cleaned = replace_specific_words(document_cleaned)
                document_cleaned = remove_page_numbers(document_cleaned)

                # Écrire le texte nettoyé dans un nouveau fichier pour les textes nettoyés
                output_folder_cleaned = os.path.join(os.path.dirname(file_path), 'cleaned_texts')
                if not os.path.exists(output_folder_cleaned):
                    os.makedirs(output_folder_cleaned)
                output_file_path_cleaned = os.path.join(output_folder_cleaned, os.path.basename(file_path))
                with open(output_file_path_cleaned, 'w', encoding="utf8") as final_doc_cleaned:
                    final_doc_cleaned.write(document_cleaned)

                print("Fichier traité avec succès :", file_path)  # Ajout d'un message d'impression

def remove_pourvoi(document):
    regex = ('(Pourvoi\sN°\d*-\d*\.\d*-[A-Z][a-z]{1,}é?è?[a-z]*\s[a-z]*è?é?[a-z]*è?é?[a-z]*\s[a-z]*é?è?[a-z]*\s[a-z]*\sè?é?[a-z]*\s{1,}\d*\s[a-z]*é?è?[a-z]*\s\d*\s{1,})')
    return re.sub(regex, (" "), document)

def remove_underscores(document):
    regex = '(\_{6,})'
    return re.sub(regex, (""), document)

def replace_acronyms(document):
    regex = '([A-Z]É[A-Z]{4,}Ç[A-Z]{3,})'
    return re.sub(regex, ("RÉPUBLIQUE FRANÇAISE"), document)

def normalize_moyens(document):
    regex = ('(Moyens\n{1,})')
    return re.sub(regex, ("Moyens. "), document)

def remove_form_feed(document):
    regex = '(\f)'
    return re.sub(regex, (""), document)

def remove_extra_spaces(document):
    regex_four = r"(\n{1,}|\s{3,})"
    result_four = re.sub(regex_four, " ", document)
    regex_deux_espaces = r"(?<!\s)\s{2}(?!\s)"
    result_four = re.sub(regex_deux_espaces, " ", result_four)
    return result_four 

def replace_specific_words(document):
    regex_words = ['Texte de la décision', 'Entête', 'Exposé du litige', 'Moyens annexés', 'Faits et procédure', 'Examen des moyens', 'Enoncé du moyen', 'Motivation', 'Réponse de la Cour', 'Dispositif']
    replace_words = ['  Texte de la décision.', 'Entête.', 'Exposé du litige.', 'Moyens annexés.', 'Faits et procédure.', 'Examen des moyens.', 'Enoncé du moyen.', 'Motivation.', 'Réponse de la Cour.', 'Dispositif.']
    for i in range(len(regex_words)):
        document = re.sub(re.escape(regex_words[i]), replace_words[i], document)
    return document


def remove_page_numbers(document):
    regex_pages = r"(\sPage \d+ /\s*\d+)"
    return re.sub(regex_pages,"", document)



normalize_files('data_base')

Token.set_extension("custom_boundary", default=False)
Token.set_extension("set_custom_B", default=False)
nlp_b = spacy.load('fr_core_news_lg')
nlp = spacy.load('fr_core_news_lg')
@spacy.Language.component("set_custom_boundary")
def set_custom_boundary(doc):
    for i, token in enumerate(doc):
        if i < len(doc) - 2 and token.text.isdigit() and doc[i+1].text == "." and doc[i+2].whitespace_:
            token._.custom_boundary = "p"
            doc[i].is_sent_start = True
            doc[i+1].is_sent_start = False
            doc[i+2].is_sent_start = False       
        if i < len(doc) - 2 and token.text.isdigit() and doc[i+1].text == "°"  and  doc[i+2].text == ")":
            token._.custom_boundary = "b"
            doc[i].is_sent_start = True
            doc[i+1].is_sent_start = False
            doc[i+1].is_sent_start = False
        if i < len(doc) - 2 and token.text.isdigit() and doc[i+1].text == "°"  and  doc[i+2].text == "/":
            token._.custom_boundary = "c"
            doc[i].is_sent_start = True
            doc[i+1].is_sent_start = False
            doc[i+1].is_sent_start = False             
        if i< len(doc) -3 and token.text == "-" or token.text == "_" and re.match(r"\d+", doc[i+1].text) :   
            doc[i].is_sent_start = False
            doc[i+1].is_sent_start = False
        if i< len(doc) and token.text == "...":
           doc[i].is_sent_start = False   
        if i< len(doc) and token.text == ",":
           doc[i].is_sent_start = False
        if i< len(doc) - 6 and re.match(r"[A-Z]{1}", token.text) and doc[i+1].text == "." and re.match(r"[A-Z]{1}", doc[i+2].text) and doc[i+3].text == "..." and re.match(r"[A-Z]{1}", doc[i+4].text) and doc[i+5].text == "..." :
           doc[i].is_sent_start = False
           doc[i+1].is_sent_start = False
           doc[i+2].is_sent_start = False
           doc[i+3].is_sent_start = False
           doc[i+4].is_sent_start = False
           doc[i+5].is_sent_start = False    
        if i< len(doc) and token.text == ".":
           doc[i].is_sent_start = False
        if i< len(doc) and token.text == "]":
           doc[i].is_sent_start = False
        if i< len(doc) and token.text == "n°":
           doc[i].is_sent_start = False 
        if i< len(doc) - 2 and token.text == "RÉPUBLIQUE" and doc[i+1].text == "FRANÇAISE" :
           doc[i].is_sent_start = True
           doc[i+1].is_sent_start = False
        if i< len(doc) -2 and token.text == "..." and re.match(r"[A-Z]{1}", doc[i+1].text) :
            doc[i].is_sent_start = False
            doc[i+1].is_sent_start = False           
        if i< len(doc) - 2 and token.text == "PEUPLE" and doc[i+1].text == "FRANÇAIS" and re.match(r".*", doc[i+2].text):
           doc[i].is_sent_start = False
           doc[i+1].is_sent_start = False
           doc[i+2].is_sent_start = True           
        if i < len(doc) - 6 and token.text == "," and doc[i+1].text == "["  and doc[i+2].text == "..." and doc[i+3].text == "]"  and doc[i+4].text == ",":
           doc[i].is_sent_start = False
           doc[i+1].is_sent_start = False
           doc[i+2].is_sent_start = False
           doc[i+3].is_sent_start = False
           doc[i+4].is_sent_start = False     
    return doc
@spacy.Language.component("set_custom_B")
def set_custom_B(doc):
    for i, token in enumerate(doc):
        if i< len(doc) -2 and token.text == ":" and re.match(r"[A-Z]{2}", doc[i+1].text):
            doc[i].is_sent_start = False
            doc[i+1].is_sent_start = False
        if i< len(doc) and token.text == "-" or token.text == "_":
           doc[i].is_sent_start = False
        if i< len(doc) and token.text == "ECLI":
           doc[i].is_sent_start = True  
        if i< len(doc) and re.match(r"CR\d+", token.text):
           doc[i].is_sent_start = False
        
        if i< len(doc) and token.text == ".":
           doc[i].is_sent_start = False
        if i< len(doc) and token.text == "n°":
           doc[i].is_sent_start = False   
    return doc

def preprocess_data(directory):
    cleaned_text_paths = []
    brute_text_paths = []
    directories_with_text = 0  # Compteur pour les répertoires contenant les deux types de fichiers texte
    num_cleaned_files = 0  # Compteur pour les fichiers dans le répertoire cleaned_texts
    num_brute_files = 0  # Compteur pour les fichiers dans le répertoire brute_texte

    for root, dirs, files in os.walk(directory):
        cleaned_text_path = os.path.join(root, 'cleaned_texts')
        brute_text_path = os.path.join(root, 'brute_texte')
        
        if os.path.exists(cleaned_text_path) and os.path.exists(brute_text_path):
            cleaned_text_paths.append(cleaned_text_path)
            brute_text_paths.append(brute_text_path)
            directories_with_text += 1
            num_cleaned_files += len(os.listdir(cleaned_text_path))
            num_brute_files += len(os.listdir(brute_text_path))
        
    return cleaned_text_paths, brute_text_paths, directories_with_text, num_cleaned_files, num_brute_files

# Exemple d'utilisation :
cleaned_paths, brute_paths, dirs_with_text, num_cleaned, num_brute = preprocess_data('data_base')
#print("Cleaned text paths found:", cleaned_paths)
#print("Brute text paths found:", brute_paths)
#print("Number of directories with both types of text files:", dirs_with_text)
#print("Number of files in cleaned_texts:", num_cleaned)
#print("Number of files in brute_texte:", num_brute)


def fileName_management(files):
    sorted_files = sorted(files)  # Tri des fichiers par ordre alphabétique des chemins
    textes_cassation = []
    textes_rejet = []
    chambres = {}
    suffixes_cassation = [] 
    suffixes_rejet = []
    print("Files:", sorted_files)  # Ajout d'un print pour afficher la liste des fichiers triés
    for file in sorted_files:
        match = re.match(r'(\d+)-(\w+)', os.path.basename(file))
        if match:
            prefix = match.group(2)
            suffix = os.path.basename(file)[match.end(2)+1:] 
            if prefix not in chambres:
                chambres[prefix] = xml.Element("group", chambre=prefix)
                print("New group created:", prefix)  # Ajout d'un print pour afficher la création d'un nouveau groupe
            CR = match.group(1)
        else:
            prefix = ""
            suffix = os.path.basename(file)
            CR = ""
        
        if CR.startswith("1"):
            textes_cassation.append(file)
            suffixes_cassation.append(suffix)
            print("File added to cassation:", file)  # Ajout d'un print pour afficher les fichiers ajoutés à la liste de cassation
        elif CR.startswith("0"):
            textes_rejet.append(file)
            suffixes_rejet.append(suffix)
            print("File added to rejet:", file)  # Ajout d'un print pour afficher les fichiers ajoutés à la liste de rejet
    
    print("Cassation files:", textes_cassation)  # Ajout d'un print pour afficher la liste des fichiers de cassation
    print("Rejet files:", textes_rejet)  # Ajout d'un print pour afficher la liste des fichiers de rejet
    print("Chambres:", chambres)  # Ajout d'un print pour afficher les groupes créés
    return textes_cassation, textes_rejet, chambres, suffixes_cassation, suffixes_rejet


def tei_header():
    root = xml.Element("TEI")
    b_text = xml.SubElement(root, "teiHeader")
    file_desc = xml.SubElement(b_text, "fileDesc")
    title_stmt = xml.SubElement(file_desc, "titleStmt")
    title_element = xml.SubElement(title_stmt, "title")
    title_element.text = " "  # Ajout d'une chaîne vide comme texte
    # Ajout de <publicationStmt> à <fileDesc>
    publication_stmt = xml.SubElement(file_desc, "publicationStmt")
    authority_element = xml.SubElement(publication_stmt, "authority")
    authority_element.text = " "
    # Ajout de <sourceDesc> à <fileDesc>
    source_desc = xml.SubElement(file_desc, "sourceDesc")
    bibl_full = xml.SubElement(source_desc, "biblFull")
    bibl_full.text = " "
    # Ajout de <titleStmt> à <biblFull> dans <sourceDesc>
    bibl_title_stmt = xml.SubElement(bibl_full, "titleStmt")
    bibl_title_element = xml.SubElement(bibl_title_stmt, "title")
    bibl_title_element.text = " "  # Ajout d'une chaîne vide comme texte
    # Ajout de <publicationStmt> à <biblFull> dans <sourceDesc>
    bibl_publication_stmt = xml.SubElement(bibl_full, "publicationStmt")
    bibl_authority_element = xml.SubElement(bibl_publication_stmt, "authority")
    bibl_authority_element.text = " "    
    return root


def corpus(textes_cassation, textes_rejet, chambres, suffixes_cassation, suffixes_rejet):
    r = tei_header()
    # Création de la structure du corpus pour les textes de cassation
    texte_cassation, chambres_cassation = process_texts(textes_cassation, suffixes_cassation, r, solution="quashing", chambres=chambres)
    # Création de la structure du corpus pour les textes de rejet
    texte_rejet, chambres_rejet = process_texts(textes_rejet, suffixes_rejet, r, solution="dismissal", chambres=chambres)
    # Retourner les textes et les groupes de chambre pour les textes de cassation et de rejet
    return r


def process_texts(text_files, suffixes, root, solution, chambres):
    # Création de l'élément texte correspondant au type de solution (cassation ou rejet)
    text_element = xml.Element("text", decision=solution)
    root.append(text_element)
    # Initialisation du dictionnaire des groupes de chambre
    chambres_dict = {chambre: xml.Element("group", chamber=chambre) for chambre in chambres}
    # Traitement de chaque fichier de texte
    for filename, suffix in zip(text_files, suffixes):
        with open(filename, "r") as file:
            text_content = file.read()
            # Création de l'élément texte pour le fichier actuel
            texte = xml.Element("text", type="appeal", fileName=suffix)
            decoupage = textual_components(text_content)
            front_element = front_text(decoupage, texte, None, nlp_b)
            texte.append(front_element)
            partie, body_element, _ = body_xml(decoupage, texte, None, nlp)
            texte.append(body_element)
            div1_element = div_paragraphe_sentences_xml(partie, body_element, nlp)
            # Récupération de la chambre à partir du nom du fichier
            chambre = filename.split("-")[1]
            # Ajout du texte à son groupe de chambre correspondant
            chambres_dict[chambre].append(texte)
    # Ajout des groupes de chambre au texte principal
    for chambre_element in sorted(chambres_dict.keys()):
        text_element.append(chambres_dict[chambre_element])
    # Retourner l'élément texte et le dictionnaire des groupes de chambre
    return text_element, chambres_dict


def textual_components(text):
    t = []
    alinea = r"\s{2}"
    division = re.split(alinea, text)
    t.extend([division[:1],division[1:2],division[2:]])
    return t


def front_text(t, texte_1,texte_2, nlp_b):
     front_element = xml.Element("front")
     pb_b_element = xml.SubElement(front_element,"pb", n="1")
     doc_title = xml.SubElement(front_element, "docTitle")
     docu = nlp_b(t[0][0])
     for ssent_i, ssent in enumerate(docu.sents):
         ecli_tokens = [tok for tok in ssent if re.match(r"ECLI", tok.text)]
         if ecli_tokens:
            ss_element = xml.SubElement(doc_title, "titlePart", type="ECLI")
            ss_element.text = ssent.text
         else:
            ss_element = xml.SubElement(doc_title, "titlePart")
            ss_element.text = ssent.text     
     return front_element

    
def body_xml(t, texte_1, texte_2, nlp):
    nlp_instance = nlp  # Créez une nouvelle variable pour stocker l'instance de nlp
    for partie in t[2:]:        
        body_element = xml.Element("body")       
        for x in t[1:2]:
            head_element = xml.Element("head", type="title")
            partie_str = ''.join(x)
            my_doc = nlp_instance(partie_str)  # Utilisez la nouvelle variable nlp_instance       
            for sssent_i, sssent in enumerate(my_doc.sents):
                if sssent.text.strip():
                   head_element.text = sssent.text
                   body_element.append(head_element)
    partie = [item.strip() for item in partie]     
    return partie, body_element, nlp_instance


def div_paragraphe_sentences_xml(partie, body_element, nlp):
    for div_i, div in enumerate(partie, start=0):
        doc = nlp(div)
        div1_element = xml.Element("div", n=str(div_i))
        body_element.append(div1_element)
        current_container = None
        encapsulated_first_s = False
        current_element = None
        for i_sent, sent in enumerate(doc.sents, start=0):
            sentences = sent.text
            if i_sent == 0:
                cleaned_text = re.sub(r"[^\w\s-]", "", sentences)
                cleaned_text = re.sub(r"\s+", "_", cleaned_text)
                cleaned_text = unicodedata.normalize('NFKD', cleaned_text).encode('ASCII', 'ignore').decode('utf-8')
                head_element = xml.Element("head", type="subTitle", interp=f"#{cleaned_text}")
                div1_element.append(head_element)
                head_element.text = sentences
            else:
                if sent[0]._.custom_boundary == "p":
                    current_element = "p"
                    current_container = None
                    for element in reversed(div1_element):
                        if element.tag == "p":
                            current_container = element
                            break
                    if current_container is None or current_container[-1].tag == "s":
                        current_container = xml.Element("p")
                        div1_element.append(current_container)
                elif sent[0]._.custom_boundary == "b":
                    current_element = "b"
                    current_container = None
                    for element in reversed(div1_element):
                        if element.tag == "b":
                            current_container = element
                            break
                    if current_container is None or current_container[-1].tag == "s":
                        current_container = xml.Element("p")
                        div1_element.append(current_container)
                elif sent[0]._.custom_boundary == "c":
                    current_element = "c"
                    current_container = None
                    for element in reversed(div1_element):
                        if element.tag == "c":
                            current_container = element
                            break
                    if current_container is None or current_container[-1].tag == "s":
                        current_container = xml.Element("p")
                        div1_element.append(current_container)
                if current_container is not None:
                    s_element = xml.SubElement(current_container, "s", n=str(i_sent - 1))
                else:
                    s_element = xml.SubElement(div1_element, "s", n=str(i_sent - 1))

                add_token_xml(div1_element, current_container, s_element, sent)

                matcher_triggers(div1_element, current_container, s_element, sent, sentences)             
    return div1_element


def add_token_xml(div1_element, current_container, s_element, sent):
    alphabet = string.ascii_uppercase
    additional_characters = string.ascii_lowercase + string.digits + "_-."
    current_combination = ['A']
    used_ids = set()
    for token_i, token in enumerate(sent):
        n = str(token_i)
        while True:
            random_chars = ''.join(random.choices(additional_characters, k=6))
            xmlid = ''.join(current_combination) + n + random_chars
            if xmlid not in used_ids:
                used_ids.add(xmlid)
                break
        add_page_xml(sent, token_i, token, s_element)
        t_element = xml.SubElement(s_element, "w",{'xml:id': xmlid, 'n': str(token_i), 'lemma': token.lemma_, 'pos': token.pos_})
        t_element.text = token.text
        for i in reversed(range(len(current_combination))):
            if current_combination[i] != 'Z':
                current_combination[i] = chr(ord(current_combination[i]) + 1)
                break
            else:
                current_combination[i] = 'A'
                if i == 0:
                    current_combination.insert(0, 'A')


                    
def add_page_xml(sent, token_i, token, s_element):
    if token.text == "Page" and token_i + 3 < len(sent) and sent[token_i + 1].text.isdigit() and sent[token_i + 2].text == "/" and sent[token_i + 3].text.isdigit():
       pb_element = xml.Element("pb", {'n': str(add_page_xml.page_count)})  # Ajouter l'attribut n avec la valeur de la page_count
       add_page_xml.page_count += 1  # Incrémentez la page_count pour la prochaine balise <pb>
       s_element.append(pb_element)
add_page_xml.page_count = 2  # Initialisez la page_count à 2



def matcher_triggers(div1_element, current_container, s_element, sent, sentences):
    annotation_elem = xml.SubElement(s_element,"s", ana="reading")
    annotation_elem.text = sentences
    nlp.max_length = 10000000
    regex_pattern = r"(?i)(ne|n\'[a-z]*)(?:\s\w+){1,}\s(que|qu\'[a-z]*)"
    matcher = spacy.matcher.Matcher(nlp.vocab)
    verb_patterns = [
         [
          {"LEMMA": verbi}, {"LEMMA": {"NOT_IN": ["que","de"]}, "OP": "{,5}"},{"LEMMA": {"IN": ["que"]}, "OP": "+"}
         ]
         for verbi in ["regretter","savoir", "apprendre", "comprendre", "remarquer", "étonner", "calculer", "sentir", "reconnaître", "ignorer", "découvrir", "avouer"]
         ]               
    verb_patterns_one = [
         [
          {"LEMMA": verbe},
          {"LEMMA": {"NOT_IN": ["que","de"]}, "OP": "{,5}"},
          {"DEP": {"IN": ["xcomp"]}, "OP": "+"}
         ]
         for verbe in ["regretter","avoir raison","remarquer", "étonner",  "reconnaître", "ignorer", "découvrir", "avouer","apprendre", "comprendre","calculer", "sentir"]
         ]              
    verb_patternscass = [
            [
             {"LEMMA": verb},
             {"LEMMA": {"NOT_IN": ["que","de"]}, "OP": "{,5}"},
             {"LEMMA": {"IN": ["de"]}, "OP": "+"}
            ]
            for verb in ["regretter","avoir raison","remarquer", "étonner",  "reconnaître", "ignorer", "découvrir", "avouer","apprendre", "comprendre","calculer", "sentir"]
            ]
    adv_rest_pattern_cass = [
            [{"LEMMA": "ne"},{"LEMMA": {"NOT_IN": ["pas", "que", "aucunement",  "seulement", "uniquement"]}, "OP": "{1,8}"},{"LEMMA": "que"}],
            [{"LEMMA": "seul", "DEP": "advmod"}],
            [{"ORTH": "seulement"}],
            [{"ORTH": "uniquement"}]
            ]                                      
    predic_aspect_pattern_cass = [
            [{"LEMMA": "ne"},{"LEMMA": {"NOT_IN": ["pas", "que", "aucunement", "et", "seulement", "uniquement"]}, "OP": "{,5}"},{"LEMMA": "plus"}]
            ]
    predic_aspect_pattern = [                           
            [ {"LEMMA": asp}]
                 for asp in ["encore", "terminer", "déjà", "commencer", "pas encore", "demeurer", "arrêter","toujours", "de nouveau", "cesser", "prolonger", "rester"]]
    sub_temp_cass=[
            [ {"LEMMA": sub_temp}]
                 for sub_temp in ["après", "avant", "tandis que", "quand", "lorsque", "une fois", "pendant que" , "à mesure que", "au moment où", "jour", "depuis que", "dès que"]]
    sub_cause_cass=[
            [ {"LEMMA": sub_cause}]
                 for sub_cause in ["puisque", "si", "quoique", "de sorte que", "bien que", "pour", "quelque", "quoi que"]]
    adv_add_cass=[
            [ {"LEMMA": adv_add}]
                 for adv_add in ["également", "aussi", "autre", "à leur tour", "nouveau"]]                       
    matcher.add("ADV_REST", adv_rest_pattern_cass)
    matcher.add("VRB_FACT", verb_patterns)
    matcher.add("VRB_FACT", verb_patternscass)
    matcher.add("VRB_FACT", verb_patterns_one)
    matcher.add("PRED_ASP", predic_aspect_pattern_cass)
    matcher.add("PRED_ASP", predic_aspect_pattern)
    matcher.add("SUB_TEMP", sub_temp_cass)
    matcher.add("SUB_CAUS", sub_cause_cass)
    matcher.add("ADV_ADDI", adv_add_cass)                       
    matches = matcher(nlp(sentences))
    for match_id, start, end in matches:
        matched_span = nlp(sentences)[start:end]
        attrs = OrderedDict()
        if match_id == matcher.vocab.strings["ADV_REST"]:
           attrs["type"] = "ADV_REST"
        elif match_id == matcher.vocab.strings["VRB_FACT"]:
             attrs["type"] = "VRB_FACT"
        elif match_id == matcher.vocab.strings["PRED_ASP"]:
             attrs["type"] = "PRED_ASP"
        elif match_id == matcher.vocab.strings["SUB_TEMP"]:
             attrs["type"] = "SUB_TEMP"
        elif match_id == matcher.vocab.strings["SUB_CAUS"]:
             attrs["type"] = "SUB_CAUS"
        elif match_id == matcher.vocab.strings["ADV_ADDI"]:
             attrs["type"] = "ADV_ADDI"                            
        #attrs["dep"] = matched_span.root.dep_
        attrs["ana"] = ""
        attrs["form"] = str(matched_span)
        attrs["lemma"] = matched_span.lemma_
        attrs["from"] = str(matched_span.start)
        if len(matched_span) > 1:
           attrs["to"] = str(matched_span.end - 1)
        dp = xml.Element("trigger", **attrs)
        s_element.append(dp)

        

def insert_pb(xml_bytes_io, xml_bytes_io_brutes):
    # Positionner les objets BytesIO au début de leurs flux de données XML
    xml_bytes_io.seek(0)
    xml_bytes_io_brutes.seek(0)

    # Vérifier le contenu XML des objets BytesIO
    print("XML in xml_bytes_io:")
    #print(xml_bytes_io.getvalue())
    print("XML in xml_bytes_io_brutes:")
    #print(xml_bytes_io_brutes.getvalue())

    tree_corp = xml.parse(xml_bytes_io)
    root_corp = tree_corp.getroot()
    tree_pb = xml.parse(xml_bytes_io_brutes)
    root_pb = tree_pb.getroot()
    
    # Utilisation de tqdm pour suivre la progression de la boucle
    with tqdm(total=len(root_pb.findall(".//s")), desc="Inserting pb tags") as pbar:
        for index, s_pb in enumerate(root_pb.findall(".//s")):
            try:
                s_corp = root_corp.findall(".//s")[index]
            except IndexError:
                print("IndexError: s_pb index", index, "is out of range")
                break  # Sortir de la boucle si l'index est en dehors de la plage
            for pb in s_pb.findall(".//pb"):
                pb_index = list(s_pb).index(pb)
                s_corp.insert(pb_index, pb)
            pbar.update(1)
    
    # Écriture du XML final
    with open("corpus_final", "wb") as f:
        xml.ElementTree(root_corp).write(f, encoding="utf-8", xml_declaration=True)


def get_files(directory):
    """
    Récupère tous les fichiers texte dans un répertoire donné et ses sous-répertoires.
    """
    files = []  # Une liste pour stocker les chemins des fichiers texte trouvés

    # Parcours récursif de tous les sous-répertoires et fichiers dans le répertoire donné
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:  # Parcours de tous les fichiers dans le répertoire courant
            if filename.endswith(".txt"):
                file_path = os.path.join(root, filename)
                files.append(file_path)  # Ajout du chemin complet du fichier à la liste
                #print("File found:", file_path)  # Débogage : Affiche le chemin du fichier trouvé
    return sorted(files)  # Retourne la liste des fichiers triés par ordre alphabétique des chemins

def main():
    nlp.add_pipe("set_custom_boundary", before="parser")
    nlp_b.add_pipe("set_custom_B", before="parser")   
    directory = 'data_base'  # Répertoire principal  

    # Récupérer tous les fichiers texte de tous les sous-répertoires pour les textes nettoyés et bruts
    cleaned_paths, brute_paths, _, _, _ = preprocess_data(directory)
    cleaned_text_files = []
    brute_text_files = []

    # Récupérer tous les fichiers texte pour les textes nettoyés
    for path in cleaned_paths:
        cleaned_text_files.extend(get_files(path))

    # Récupérer tous les fichiers texte pour les textes bruts
    for path in brute_paths:
        brute_text_files.extend(get_files(path))

    # Ajouter la barre de progression pour la lecture des fichiers texte nettoyés
    with tqdm(total=len(cleaned_text_files), desc="Processing cleaned texts") as pbar:
        for path in cleaned_text_files:
            # Traiter chaque fichier
            pbar.update(1)

    # Ajouter la barre de progression pour la lecture des fichiers texte bruts
    with tqdm(total=len(brute_text_files), desc="Processing raw texts") as pbar:
        for path in brute_text_files:
            # Traiter chaque fichier
            pbar.update(1)

    # Traiter tous les fichiers texte de cleaned_texts comme un ensemble
    tc_cleaned, tr_cleaned, ch_cleaned, sc_cleaned, sr_cleaned = fileName_management(cleaned_text_files)
    root_cleaned = corpus(tc_cleaned, tr_cleaned, ch_cleaned, sc_cleaned, sr_cleaned)
    tree_cleaned = xml.ElementTree(root_cleaned)
    xml.indent(root_cleaned, space="\t")    
    # Écriture du XML en mémoire pour les textes nettoyés
    xml_bytes_io_cleaned = io.BytesIO()
    tree_cleaned.write(xml_bytes_io_cleaned, encoding="utf-8", xml_declaration=True)
    print("XML written to memory for cleaned texts.")
    # Écriture du XML réel pour les textes nettoyés
    with open("cleaned_texts.xml", "wb") as f:
        tree_cleaned.write(f, encoding="utf-8", xml_declaration=True)
        print("XML written to disk for cleaned texts.")

    # Traiter tous les fichiers texte de brute_texte comme un ensemble
    tc_brutes, tr_brutes, ch_brutes, sc_brutes, sr_brutes = fileName_management(brute_text_files)
    root_brute = corpus(tc_brutes, tr_brutes, ch_brutes, sc_brutes, sr_brutes)
    tree_brute = xml.ElementTree(root_brute)
    xml.indent(root_brute, space="\t")    
    # Écriture du XML en mémoire pour les textes bruts
    xml_bytes_io_brute = io.BytesIO()
    tree_brute.write(xml_bytes_io_brute, encoding="utf-8", xml_declaration=True)
    print("XML written to memory for raw texts.")
    # Écriture du XML réel pour les textes bruts
    with open("brute_texts.xml", "wb") as f:
        tree_brute.write(f, encoding="utf-8", xml_declaration=True)
        print("XML written to disk for raw texts.")
    
    # Insérer le point de rupture ici
    insert_pb(xml_bytes_io_cleaned, xml_bytes_io_brute)

# Appeler la fonction main
main()
