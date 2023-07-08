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
import string
from spacy.tokens import Token
from spacy.tokens import Doc
import numpy as np
import pandas as pd
#from colorama import Fore, Back, Style
from spacy.matcher import PhraseMatcher
import itertools
import random
import unicodedata
#############Corpus
from collections import OrderedDict

nlp = spacy.load('fr_core_news_lg')
Token.set_extension("custom_boundary", default=False)
@spacy.Language.component("set_custom_boundary")
def set_custom_boundary(doc):
    for i, token in enumerate(doc):

        if i < len(doc) - 2 and token.text.isdigit() and doc[i+1].text == "." and doc[i+2].whitespace_:
            token._.custom_boundary = "p"
            doc[i].is_sent_start = True
            doc[i+1].is_sent_start = False
            doc[i+2].is_sent_start = False
        
        if i < len(doc) - 2 and token.text.isdigit() and doc[i+1].text == "°" and doc[i+2].text == "/":
            token._.custom_boundary = "b"
            doc[i].is_sent_start = True
            doc[i+1].is_sent_start = False
            doc[i+2].is_sent_start = False
   
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
        if i< len(doc) and token.text == "[" and re.match(r"[A-Z]{1,}", doc[i+1].text):
           doc[i].is_sent_start = False
           doc[i+1].is_sent_start = False
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
nlp_b = spacy.load('fr_core_news_lg')
Token.set_extension("set_custom_B", default=False)
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

def generate_xml():
    nlp.add_pipe("set_custom_boundary", before="parser")
    nlp_b.add_pipe("set_custom_B", before="parser")
    files = sorted(glob.glob("*.txt"))

    
    root = xml.Element("TEI")#, xmlns="http://www.tei-c.org/ns/1.0" 
    b_text = xml.SubElement(root, "teiHeader")
    file_desc = xml.SubElement(b_text, "fileDesc")

    title_stmt = xml.SubElement(file_desc, "titleStmt")
    title_element = xml.SubElement(title_stmt, "title")
    title_element.text = ""  # Ajout d'une chaîne vide comme texte

    # Ajout de <publicationStmt> à <fileDesc>
    publication_stmt = xml.SubElement(file_desc, "publicationStmt")
    authority_element = xml.SubElement(publication_stmt, "authority")

    # Ajout de <sourceDesc> à <fileDesc>
    source_desc = xml.SubElement(file_desc, "sourceDesc")
    bibl_full = xml.SubElement(source_desc, "biblFull")

    # Ajout de <titleStmt> à <biblFull> dans <sourceDesc>
    bibl_title_stmt = xml.SubElement(bibl_full, "titleStmt")
    bibl_title_element = xml.SubElement(bibl_title_stmt, "title")
    bibl_title_element.text = ""  # Ajout d'une chaîne vide comme texte

    # Ajout de <publicationStmt> à <biblFull> dans <sourceDesc>
    bibl_publication_stmt = xml.SubElement(bibl_full, "publicationStmt")
    bibl_authority_element = xml.SubElement(bibl_publication_stmt, "authority")

                    
    CLEAN_TEXT= []
    chambres = {}
    texte = xml.SubElement(root, "text", solution="cassation")
    #composite = xml.SubElement(texte,"front")
    #castList = xml.SubElement(composite, "castList")
    #cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Entete"})
    #role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
    #cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Expose_du_litige"})
    #role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
   # cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Moyens"})
   # role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
    #cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Motivation"})
    #role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
    #cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Dispositif"})
    #role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
    #cast_item = xml.SubElement(castList,"castItem", {'xml:id':"Documents_de_communication"})
    #role = xml.SubElement(cast_item, "role")
    #role.text= "structure du raisonnement"
    for file in files:
         match = re.match(r'(\d+)-(\w+)', file)
         if match:
            prefix = match.group(2)
            suffix = file[match.end(2)+1:]  # Extraire le reste du nom de fichier après le préfixe
         else:
            prefix = ""
            suffix = file

        # nouvelle balise chambre
         if prefix not in chambres:
            chambres[prefix] = xml.Element("group", chambre=prefix)

         chambre_element = chambres[prefix]

         with open(file, "r", encoding="utf8") as f:
             text = f.read()
             division = r"\s{2}"

             # Expression régulière pour la séquence "ne + un à deux mots inconnus + que"
             #regex_pattern = r"ne(?:\s\w+){1,2}\sque"

             #matches = re.findall(regex_pattern, text)
             #print(matches)
             #exit()
             dive = re.split(division, text)
             compteur = 1
             CLEAN_TEXT.append(dive)

             pourvoi_element = xml.Element("text", type="pourvoi", fileName=suffix)
             chambre_element.append(pourvoi_element)
         for i in CLEAN_TEXT:
                div_pourvoi = i[:1]
                div_pour = i[1:]
                t = []
                t.append(div_pourvoi)
                t.append(div_pour)
            
         for s in t[:1]:
             div3_element = xml.Element("front")
             pb_b_element = xml.SubElement(div3_element,"pb", n="1")
             pourvoi_element.append(div3_element)
             iii = ""
             iiiii = iii.join(s)
             docu = nlp_b(iiiii)
             doc_title = xml.SubElement(div3_element, "docTitle")
             for ssent_i, ssent in enumerate(docu.sents):
                 ecli_tokens = [tok for tok in ssent if re.match(r"ECLI", tok.text)]
                 if ecli_tokens:
                    ss_element = xml.SubElement(doc_title, "titlePart", type="ECLI")
                    ss_element.text = ssent.text
                 else:
                     ss_element = xml.SubElement(doc_title, "titlePart")
                     ss_element.text = ssent.text
                 my_page = None
                 my_indx = -1
                 for token_i, token in enumerate(ssent):
                     if token.text == "Page" and token_i + 4 < len(ssent) and ssent[token_i + 1].text.isdigit() and ssent[token_i + 2].text == "/" and ssent[token_i + 3].text.isdigit():
                        # La séquence recherchée a été trouvée
                        print("Match trouvé :", token.text, ssent[token_i + 1].text, ssent[token_i + 2].text, ssent[token_i + 3].text)
                        my_page = xml.Element("pb")
                        ss_element.insert(my_indx + 1, my_page)
                        (pb_index + 1, pb_element)

         for partie in t[1:]:
             div_element = xml.Element("body")
             pourvoi_element.append(div_element)
              
             dive = [item.strip() for item in dive]
             for x in dive[1:2]:
                 head_element = xml.Element("head", type="title")
                 my_doc = nlp(x)
                 
                 for sssent_i, sssent in enumerate(my_doc.sents):
                     head_element.text = sssent.text
                     div_element.append(head_element)
                   

             for ind_i, ind in enumerate(dive[2:], start=-0):
                 div1_element = xml.Element("div", n=str(ind_i))
                 div_element.append(div1_element)

                 doc = nlp(ind)
             
                 current_container = None
                 encapsulated_first_s = False
                 current_element = None
                 

                 for i_sent, sent in enumerate(doc.sents, start=-1):
                    sentences = sent.text
                    if i_sent == 0:
                        cleaned_text = re.sub(r"[^\w\s-]", "", sentences)
                        cleaned_text = re.sub(r"\s+", "_", cleaned_text)
                        cleaned_text = unicodedata.normalize('NFKD', cleaned_text).encode('ASCII', 'ignore').decode('utf-8')

                        head_element = xml.Element("head", type="subtitle", interp= f"#{cleaned_text}")
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
                                current_container = xml.Element("p", ana="branche")
                                div1_element.append(current_container)

                        if current_container is not None:
                            s_element = xml.SubElement(current_container, "s", n=str(i_sent))
                            
                        else:
                            
                            s_element = xml.SubElement(div1_element, "s", n=str(i_sent))
                        annotation_elem = xml.SubElement(s_element,"s", ana="reading")
                        annotation_elem.text = sentences
                        nlp.max_length = 10000000
                        regex_pattern = r"(?i)(ne|n\'[a-z]*)(?:\s\w+){1,3}\s(que|qu\'[a-z]*)"

                        # Création du PhraseMatcher
                        phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")

                        patterns = {
                            "VRB_FACT": ["avoir raison", "savoir", "apprendre", "comprendre", "remarquer", "étonner", "calculer",
                                          "sentir", "reconnaître", "ignorer", "découvrir", "avouer"],
                            "SUB_TEMP": ["après", "avant", "tandis que", "quand", "lorsque", "fois", "pendant", "à mesure que",
                                         "au moment où", "jour", "depuis que", "dès que"],
                            "SUB_CAUS": ["puisque", "si", "quoique", "de sorte que", "bien que", "pour", "quelque", "quoi que"],
                            "ADV_ADDI": ["également", "aussi", "autre", "à leur tour", "nouveau"],
                            "ADV_REST": ["seul", "seulement", "uniquement"],
                            "PRED_ASP": ["encore", "plus", "terminer", "déjà", "commencer", "pas encore", "demeurer", "arrêter",
                                         "toujours", "de nouveau", "cesser", "prolonger", "rester"]
                        }

                        # Ajout des modèles de phrases au PhraseMatcher
                        for category, phrases in patterns.items():
                            category_patterns = [nlp(phrase) for phrase in phrases]
                            phrase_matcher.add(category, None, *category_patterns)

                        # Recherche des matches avec le PhraseMatcher
                        matches = phrase_matcher(nlp(sentences))

                        # Traitement des matches
                        for match_id, start, end in matches:
                            match_category = nlp.vocab.strings[match_id]
                            span = nlp(sentences)[start:end]
                            my_lemma = span.lemma_
                            my_scope = str(start)
                            attrs = OrderedDict()
                            attrs["type"] = match_category
                            attrs["ana"] = ""
                            attrs["form"] = str(span)
                            attrs["lemma"] = my_lemma
                            #attrs["interp"] = f"#{cleaned_text}"
                            attrs["from"] = my_scope
                            if len(span) > 1:
                                attrs["to"] = str(end - 1)
                            my_dp = xml.Element("trigger", **attrs)
                            s_element.append(my_dp)

                        # Recherche des correspondances avec la regex
                        

                        # Traitement des correspondances
                        matches = re.finditer(regex_pattern, sentences)

                        for match in matches:
                            span_text = match.group()
                            span_start, span_end = match.span()

                            # Utilisation de spaCy pour obtenir les tokens de la phrase
                            doc = nlp(sentences)
                            tokens = [token for token in doc]

                            # Recherche de l'index de début et de fin des tokens correspondant à la correspondance
                            start_token_idx = None
                            end_token_idx = None

                            for idx, token in enumerate(tokens):
                                if token.idx == span_start:
                                    start_token_idx = idx
                                if token.idx + len(token) == span_end:
                                    end_token_idx = idx

                            if start_token_idx is not None and end_token_idx is not None:
                                start = tokens[start_token_idx].i
                                end = tokens[end_token_idx].i

                                attrs = OrderedDict()
                                attrs["type"] = "ADV_REST"
                                attrs["ana"] = ""
                                attrs["form"] = span_text
                                attrs["lemma"] = span_text
                                #attrs["interp"] = f"#{cleaned_text}"
                                attrs["from"] = str(start)
                                attrs["to"] = str(end)

                                my_d = xml.Element("trigger", **attrs)
                                s_element.append(my_d)

                        pb_element = None
                        pb_index = -1
                        
                        alphabet = string.ascii_uppercase
                        additional_characters = string.ascii_lowercase + string.digits + "_-."  # Caractères supplémentaires autorisés
                        current_combination = ['A']  # Commencer par une seule lettre
                        used_ids = set()  # Ensemble pour stocker les ids déjà utilisés

                        for token_i, token in enumerate(sent):
                            n = str(token_i)
                            while True:
                                random_chars = ''.join(random.choices(additional_characters, k=6))  # Générer 6 caractères aléatoires supplémentaires
                                xmlid = ''.join(current_combination) + n + random_chars
                                if xmlid not in used_ids:  # Vérifier si l'id est déjà utilisé
                                    used_ids.add(xmlid)  # Ajouter l'id à l'ensemble des ids utilisés
                                    break

                            t_element = xml.SubElement(s_element, "w", {'xml:id': xmlid, 'n': str(token_i), 'lemma': token.lemma_, 'pos': token.pos_})
                            t_element.text = token.text

                            # Générer la prochaine combinaison unique
                            for i in reversed(range(len(current_combination))):
                                if current_combination[i] != 'Z':
                                    current_combination[i] = chr(ord(current_combination[i]) + 1)
                                    break
                                else:
                                    current_combination[i] = 'A'
                                    if i == 0:
                                        current_combination.insert(0, 'A')

                            if token.text == "Page" and token_i + 4 < len(sent) and sent[token_i + 1].text.isdigit() and sent[token_i + 2].text == "/" and sent[token_i + 3].text.isdigit():
                                pb_element = xml.Element("pb")
                                pb_index = token_i + 3
                                compteur += 1  # Incrémente le compteur

                        if pb_element is not None and pb_index + 1 < len(sent):
                            s_element.insert(pb_index + 1, pb_element) 
                            pb_element.set("n", f"n {compteur}")
                     

    for chambre_element in sorted(chambres.values(), key=lambda x: x.attrib["chambre"]):
        texte.append(chambre_element)

    tree = xml.ElementTree(root)
    xml.indent(tree, space="\t", level=0)
    with open("annotation-presupp.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
#generate_xml()
#exit()

####REJET



def GENERATE():   
    nlp.add_pipe("set_custom_boundary", before="parser")
    nlp_b.add_pipe("set_custom_B", before="parser")
    my_files =sorted(glob.glob("rejet_corp/*.txt"))
    CLEAN_TEXT =[]
    chambres = {}
    root = xml.parse("annotation-presupp.xml").getroot()
    texte = xml.Element("text", solution="rejet")
    root.append(texte)
    #balise = xml.SubElement(b_text, "text")
    
    for file in my_files:
        match = re.match(r'rejet_corp/(\d+)-(\w+)', file)
        if match:
            prefix = match.group(2)
            suffix = file[match.end(2)+1:]  # Extraire le reste du nom de fichier après le préfixe
        else:
            prefix = ""
            suffix = file
        if prefix not in chambres:
           chambres[prefix] = xml.Element("group", chambre=prefix)
        chambre_element = chambres[prefix]
        with open(file, "r", encoding="utf8") as f:
             text = f.read()
             division = r"\s{2}"

             # Expression régulière pour la séquence "ne + un à deux mots inconnus + que"
             #regex_pattern = r"ne(?:\s\w+){1,2}\sque"

             #matches = re.findall(regex_pattern, text)
             #print(matches)
             #exit()
             dive = re.split(division, text)
             compteur = 1
             CLEAN_TEXT.append(dive)

             pourvoi_element = xml.Element("text", type="pourvoi", fileName=suffix)
             chambre_element.append(pourvoi_element)
        for i in CLEAN_TEXT:
             div_pourvoi = i[:1]
             div_pour = i[1:]
             t = []
             t.append(div_pourvoi)
             t.append(div_pour)
            
        for s in t[:1]:
            div3_element = xml.Element("front")
            pb_b_element = xml.SubElement(div3_element,"pb", n="1")
            pourvoi_element.append(div3_element)
            iii = ""
            iiiii = iii.join(s)
            docu = nlp_b(iiiii)
            doc_title = xml.SubElement(div3_element, "docTitle")
            for ssent_i, ssent in enumerate(docu.sents):
                ecli_tokens = [tok for tok in ssent if re.match(r"ECLI", tok.text)]
                if ecli_tokens:
                   ss_element = xml.SubElement(doc_title, "titlePart", type="ECLI")
                   ss_element.text = ssent.text
                else:
                    ss_element = xml.SubElement(doc_title, "titlePart")
                    ss_element.text = ssent.text
                my_page = None
                my_indx = -1
                for token_i, token in enumerate(ssent):
                    if token.text == "Page" and token_i + 4 < len(ssent) and ssent[token_i + 1].text.isdigit() and ssent[token_i + 2].text == "/" and ssent[token_i + 3].text.isdigit():
                        # La séquence recherchée a été trouvée
                        print("Match trouvé :", token.text, ssent[token_i + 1].text, ssent[token_i + 2].text, ssent[token_i + 3].text)
                        my_page = xml.Element("pb")
                        ss_element.insert(my_indx + 1, my_page)
                        (my_indx + 1, my_page) 
                        


        for partie in t[1:]:
            div_element = xml.Element("body")
            pourvoi_element.append(div_element)
              
            dive = [item.strip() for item in dive]
            for x in dive[1:2]:
                head_element = xml.Element("head", type="title")
                my_doc = nlp(x)
                 
                for sssent_i, sssent in enumerate(my_doc.sents):
                    head_element.text = sssent.text
                    div_element.append(head_element)
                 

            for ind_i, ind in enumerate(dive[2:], start=0):
                div1_element = xml.Element("div", n=str(ind_i))
                div_element.append(div1_element)

                doc = nlp(ind)
             
                current_container = None
                encapsulated_first_s = False
                current_element = None
                for i_sent, sent in enumerate(doc.sents, start=-1):
                    sentences = sent.text
                    if i_sent == 0:
                        cleaned_text = re.sub(r"[^\w\s-]", "", sentences)
                        cleaned_text = re.sub(r"\s+", "_", cleaned_text)
                        cleaned_text = unicodedata.normalize('NFKD', cleaned_text).encode('ASCII', 'ignore').decode('utf-8')

                        head_element = xml.Element("head", type="subtitle", interp= f"#{cleaned_text}")
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
                                current_container = xml.Element("p", ana="branche")
                                div1_element.append(current_container)

                        if current_container is not None:
                            s_element = xml.SubElement(current_container, "s", n=str(i_sent))
                            
                        else:
                            
                            s_element = xml.SubElement(div1_element, "s", n=str(i_sent))
                        annotation_elem = xml.SubElement(s_element,"s", ana="reading")
                        annotation_elem.text = sentences
                        nlp.max_length = 10000000
                        regex_pattern = r"(?i)(ne|n\'[a-z]*)(?:\s\w+){1,3}\s(que|qu\'[a-z]*)"

                        # Création du PhraseMatcher
                        phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")

                        patterns = {
                            "VRB_FACT": ["avoir raison", "savoir", "apprendre", "comprendre", "remarquer", "étonner", "calculer",
                                          "sentir", "reconnaître", "ignorer", "découvrir", "avouer"],
                            "SUB_TEMP": ["après", "avant", "tandis que", "quand", "lorsque", "fois", "pendant", "à mesure que",
                                         "au moment où", "jour", "depuis que", "dès que"],
                            "SUB_CAUS": ["puisque", "si", "quoique", "de sorte que", "bien que", "pour", "quelque", "quoi que"],
                            "ADV_ADDI": ["également", "aussi", "autre", "à leur tour", "nouveau"],
                            "ADV_REST": ["seul", "seulement", "uniquement"],
                            "PRED_ASP": ["encore", "plus", "terminer", "déjà", "commencer", "pas encore", "demeurer", "arrêter",
                                         "toujours", "de nouveau", "cesser", "prolonger", "rester"]
                         }

                        # Ajout des modèles de phrases au PhraseMatcher
                        for category, phrases in patterns.items():
                            category_patterns = [nlp(phrase) for phrase in phrases]
                            phrase_matcher.add(category, None, *category_patterns)

                         # Recherche des matches avec le PhraseMatcher
                        matches = phrase_matcher(nlp(sentences))

                        # Traitement des matches
                        for match_id, start, end in matches:
                            match_category = nlp.vocab.strings[match_id]
                            span = nlp(sentences)[start:end]
                            my_lemma = span.lemma_
                            my_scope = str(start)
                            attrs = OrderedDict()
                            attrs["type"] = match_category
                            attrs["ana"] = ""
                            attrs["form"] = str(span)
                            attrs["lemma"] = my_lemma
                            #attrs["interp"] = f"#{cleaned_text}"
                            attrs["from"] = my_scope
                            if len(span) > 1:
                               attrs["to"] = str(end - 1)
                            my_dp = xml.Element("trigger", **attrs)
                            s_element.append(my_dp)
 
                         # Recherche des correspondances avec la regex
                        

                         # Traitement des correspondances
                        matches = re.finditer(regex_pattern, sentences)

                        for match in matches:
                            span_text = match.group()
                            span_start, span_end = match.span()

                             # Utilisation de spaCy pour obtenir les tokens de la phrase
                            doc = nlp(sentences)
                            tokens = [token for token in doc]

                             # Recherche de l'index de début et de fin des tokens correspondant à la correspondance
                            start_token_idx = None
                            end_token_idx = None

                            for idx, token in enumerate(tokens):
                                if token.idx == span_start:
                                   start_token_idx = idx
                                if token.idx + len(token) == span_end:
                                   end_token_idx = idx

                            if start_token_idx is not None and end_token_idx is not None:
                               start = tokens[start_token_idx].i
                               end = tokens[end_token_idx].i

                               attrs = OrderedDict()
                               attrs["type"] = "ADV_REST"
                               attrs["ana"] = ""
                               attrs["form"] = span_text
                               attrs["lemma"] = span_text
                               #attrs["interp"] = f"#{cleaned_text}"
                               attrs["from"] = str(start)
                               attrs["to"] = str(end)

                               my_d = xml.Element("trigger", **attrs)
                               s_element.append(my_d)

                        pb_element = None
                        pb_index = -1
                        
                        alphabet = string.ascii_uppercase
                        additional_characters = string.ascii_lowercase + string.digits + "_-."  # Caractères supplémentaires autorisés
                        current_combination = ['A']  # Commencer par une seule lettre
                        used_ids = set()  # Ensemble pour stocker les ids déjà utilisés

                        for token_i, token in enumerate(sent):
                            n = str(token_i)
                            while True:
                                random_chars = ''.join(random.choices(additional_characters, k=6))  # Générer 6 caractères aléatoires supplémentaires
                                xmlid = ''.join(current_combination) + n + random_chars
                                if xmlid not in used_ids:  # Vérifier si l'id est déjà utilisé
                                   used_ids.add(xmlid)  # Ajouter l'id à l'ensemble des ids utilisés
                                   break

                            t_element = xml.SubElement(s_element, "w", {'xml:id': xmlid, 'n': str(token_i), 'lemma': token.lemma_, 'pos': token.pos_})
                            t_element.text = token.text

                            # Générer la prochaine combinaison unique
                            for i in reversed(range(len(current_combination))):
                                if current_combination[i] != 'Z':
                                   current_combination[i] = chr(ord(current_combination[i]) + 1)
                                   break
                                else:
                                    current_combination[i] = 'A'
                                    if i == 0:
                                       current_combination.insert(0, 'A')

                            if token.text == "Page" and token_i + 4 < len(sent) and sent[token_i + 1].text.isdigit() and sent[token_i + 2].text == "/" and sent[token_i + 3].text.isdigit():
                               pb_element = xml.Element("pb")
                               pb_index = token_i + 3
                               compteur += 1  # Incrémente le compteur

                        if pb_element is not None and pb_index + 1 < len(sent):
                           s_element.insert(pb_index + 1, pb_element) 
                           pb_element.set("n", f"n {compteur}")
                     
                   

    for chambre_element in sorted(chambres.values(), key=lambda x: x.attrib["chambre"]):
        texte.append(chambre_element)

    tree = xml.ElementTree(root)
    xml.indent(tree, space="\t", level=0)
    with open("camp-annot-presupp.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
GENERATE()
#############Le temps d'essai




files = glob.glob("*.txt")

my_files = glob.glob("rejet_corp/*.txt")
 
def normalization():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex = ('(Pourvoi\sN°\d*\-\d*\.\d*\-[A-Z][a-z]{1,}é?è?[a-z]*\s[a-z]*è?é?[a-z]*è?é?[a-z]*\s[a-z]*é?è?[a-z]*\s[a-z]*\sè?é?[a-z]*\s{1,}\d*\s[a-z]*é?è?[a-z]*\s\d*\s{1,})')
             result = re.sub(regex, (" "), document)
             final_doc.write(result)
#normalization()


       
def normal_two():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex_two = '(\_{6,})'
             result_two = re.sub(regex_two, (""), document)
             final_doc.write(result_two)
#normal_two()


def normal_three():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex = '([A-Z]É[A-Z]{4,}Ç[A-Z]{3,})'
             result = re.sub(regex, ("RÉPUBLIQUE FRANÇAISE"), document)
             final_doc.write(result)
#normal_three()

def normal_moyens():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex = ('(Moyens\n{1,})')
             result = re.sub(regex, ("Moyens. "), document)
             final_doc.write(result)
#normal_moyens()


def normal_F():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex = ('(\f)')
             result = re.sub(regex, (""), document)
             final_doc.write(result)
#normal_F()

def normal_four():
    for file in files + my_files:
        with open(file, "r", encoding="utf8") as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")
             regex_four = r"(\n{1,}|\s{3,})"
             result_four = re.sub(regex_four, " ", document)
             regex_deux_espaces = r"(?<!\s)\s{2}(?!\s)"
             result_four = re.sub(regex_deux_espaces, " ", result_four)
             final_doc.write(result_four)
#normal_four()


def normal_punct():
    for file in files + my_files:
        with open(file, "r", encoding="utf8")as f:
             document = f.read()
             final_doc = open(file,'w', encoding="utf8")

             regex_words = ['Texte de la décision','Entête', 'Exposé du litige','Moyens annexés', 'Faits et procédure', 'Examen des moyens', 'Enoncé du moyen', 'Motivation', 'Réponse de la Cour', 'Dispositif']
             replace_words = ['  Texte de la décision.','Entête.', 'Exposé du litige.','Moyens annexés.', 'Faits et procédure.', 'Examen des moyens.', 'Enoncé du moyen.', 'Motivation.', 'Réponse de la Cour.', 'Dispositif.']

             for i in range(len(regex_words)):
                 document = re.sub(re.escape(regex_words[i]), replace_words[i], document)

             final_doc.write(document)

#normal_punct()
