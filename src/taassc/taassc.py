"""
This fork was created by @MikiTwenty (michele.ventimiglia01@gmail.com) on Fri May 31 00:00:00 2024

This original script builds on TAASSC 2.0.0.58, which was used in Kyle et al. 2021a,b.
The data for those publications were processed using:
- TAASSC 2.0.0.58
- Python version 3.7.3
- spaCy version 2.1.8
- spaCy `en_core_web_sm` model version 2.1.0.

This version of the code is part of a project designed to:
-  Make a more user-friendly interface (including a Python package, online tool, and a desktop tool).
-  Rnsure that the tags are as accurate as possible.

Info:
- The Tool for the Automatic Analysis of Syntactic Sophistication and Complexity (text analysis program).
- Copyright (C) 2020 - Kristopher Kyle

Licence:
- Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). See https://creativecommons.org/licenses/by-nc-sa/4.0/ for a summary of the license (and a link to the full license).
"""

# Standard Lbrary
import os
import re
import sys
import glob
import logging
from xml.dom import minidom
import xml.etree.ElementTree as ET
from typing import List, Any, Union, Dict

# Set current working directory to the directory of the script
script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.chdir(script_dir)

# Set logger
logging.basicConfig(
    level = logging.INFO,
    format = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    handlers = [
        logging.FileHandler('taassc.log', mode='a'),
        logging.StreamHandler()])
logger = logging.getLogger('TAASSC')

if __name__ == '__main__':
    logger.warning(f"This script should not be run as main!")

logger.info(f"Working on folder '{script_dir}'")
DATA_PATH = 'data'

logger.info(f"Python v: {sys.version}")

# Third-Party Packages
logger.info(f"Importing third-party packages...")
try:
    import spacy
    from typeguard import typechecked
    from lexical_diversity import lex_div as ld
    logger.info(f"Third-party packages imported.")
    logger.info(f"spaCy v: {spacy.__version__}")
except Exception as e:
    try:
        logger.info(f"Installing third-party packages.")
        os.system('python -m pip install --upgrade pip setuptools spacy')
        import spacy
        from typeguard import typechecked
        from lexical_diversity import lex_div as ld
        logger.info(f"Third-party packages installed and imported.")
        logger.info(f"spaCy v: {spacy.__version__}")
    except Exception as e:
        logger.critical(f"Failed to import third-party packages: {e}")
        raise


# Load spaCy model
try:
    logger.info(f"Loading spaCy model 'en_core_web_trf'...")
    nlp = spacy.load("en_core_web_trf")
    nlp.max_length = 1728483
    logger.info(f"spaCy model 'en_core_web_trf' loaded with max lenght '{nlp.max_length}'...")
except:
    logger.info(f"Downloading spaCy model 'en_core_web_trf'...")
    try:
        os.system("python -m spacy download en_core_web_trf")
        logger.info(f"Loading spaCy model 'en_core_web_trf'...")
        nlp = spacy.load("en_core_web_trf")
        nlp.max_length = 1728483
        logger.info(f"spaCy model 'en_core_web_trf' loaded with max lenght '{nlp.max_length}'...")
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {e}")
        raise

# Load lists
logger.info(f"Loading lists...")
try:
    semantic_noun = open(f"{DATA_PATH}/lists_LGR/semantic_class_noun.txt").read().split("\n")
    semantic_verb = open(f"{DATA_PATH}/lists_LGR/semantic_class_verb.txt").read().split("\n")
    semantic_adj = open(f"{DATA_PATH}/lists_LGR/semantic_class_adj.txt").read().split("\n")
    semantic_adv = open(f"{DATA_PATH}/lists_LGR/semantic_class_adverb_5-25-20.txt").read().split("\n")
    nominal_stop = open(f"{DATA_PATH}/lists_LGR/nom_stop_list_edited.txt").read().split("\n")
    logger.info(f"Lists loaded.")
except Exception as e:
    logger.error(f"Failed to load lists: {e}")
    raise

@typechecked
def list_dict(
        words_list: List[str]
    ) -> dict:
    """
    Create dictionaries from tab-separated files.\n
    ---
    ### Args
    - `words_list` (`List[str]`): the words list.\n
    ---
    ### Returns
    - `dict`: the dictionary.
    """
    return {y: l[0] for x in words_list for l in [x.split("\t")] for y in l[1:]}

logger.info(f"Creating dictionaries...")
try:
    noun_dict = list_dict(semantic_noun)
    verb_dict = list_dict(semantic_verb[:7])
    that_verb_dict = list_dict(semantic_verb[7:11])
    to_verb_dict = list_dict(semantic_verb[11:16])
    phrasal_verb_dict = list_dict(semantic_verb[16:])
    adj_dict = list_dict(semantic_adj)
    adv_dict = list_dict(semantic_adv)
    logger.info(f"Dictionaries created.")
except Exception as e:
    logger.error(f"Failed to create dictionaries: {e}")
    raise

categories = {}

@typechecked
def mini_d(
        category_name: str,
        category_list: list
    ) -> None:
    """
    Map each item in a list to a category name.\n
    ---
    ### Args
    - `category_name` (`str`): the category name.
    - `category_list` (`list`): the category items list.
    """
    for x in category_list:
        categories[x] = category_name


logger.info(f"Mapping items to categories...")
try:
    mini_d("main_tag", "nn_all prep_phrase verb pp_all wh_relative_clause".split())
    mini_d("main_tag2", ["all_phrasal_verbs"])
    mini_d("spec_tag1", "nominalization pp1 pp2 pp3 pp3_it pp_indefinite pp_demonstrative cc_phrase cc_clause wh_question past_tense perfect_aspect non_past_tense jj_attributive jj_predicative discourse_particle place_adverbials time_adverbials conjuncts_adverb downtoners_adverb hedges_adverb amplifiers_adverb emphatics wh_clause wh_relative_subj_clause wh_relative_obj_clause wh_relative_prep_clause that_relative_clause that_complement_clause".split())
    mini_d("spec_tag2", "pv_do split_aux be_mv that_verb_clause that_adjective_clause that_noun_clause".split())
    mini_d("spec_tag3", "adverbial_subordinator_causitive adverbial_subordinator_conditional adverbial_subordinator_other agentless_passive by_passive".split())
    mini_d("spec_tag4", ["contraction", "to_clause"])
    mini_d("spec_tag5", "modal_possibility modal_necessity modal_predictive to_clause_noun to_clause_verb to_clause_adjective".split())
    mini_d("spec_tag6", ["past_participial_clause", "complementizer_that0"])
    mini_d("semantic_tag1", "nn_animate nn_cognitive nn_concrete nn_technical nn_quantity nn_place nn_group nn_abstract activity_verb communication_verb mental_verb causation_verb occurrence_verb existence_verb aspectual_verb intransitive_activity_phrasal_verb intransitive_occurence_phrasal_verb copular_phrasal_verb intransitive_aspectual_phrasal_verb transitive_activity_phrasal_verb transitive_mental_phrasal_verb transitive_communication_phrasal_verb size_attributive_adj time_attributive_adj color_attributive_adj evaluative_attributive_adj relational_attributive_adj topical__attributive_adj attitudinal_adj likelihood_adj certainty_adj ability_willingness_adj personal_affect_adj ease_difficulty_adj evaluative_adj attitudinal_adverb factive_adverb likelihood_adverb nonfactive_adverb that_verb_clause_nonfactive that_verb_clause_attitudinal that_verb_clause_factive that_verb_clause_likelihood that_noun_clause_nonfactive that_noun_clause_attitudinal that_noun_clause_factive that_noun_clause_likelihood to_adjective_clause_certainty to_adjective_clause_ability_willingness to_adjective_clause_personal_affect to_adjective_clause_ease_difficulty to_adjective_clause_evaluative that_adjective_clause_attitudinal that_adjective_clause_likelihood".split())
    mini_d("semantic_tag2", "to_clause_verb_to_speech_act to_clause_verb_cognition to_clause_verb_desire to_clause_verb_to_causative to_clause_verb_probability to_clause_adjective_certainty to_clause_adjective_ability_willingness to_clause_adjective_personal_affect to_clause_adjective_ease_difficulty to_clause_adjective_evaluative".split())
    mini_d("other", "wrd_length nwords mattr".split())
    logger.info(f"Items to categories mapped.")
except Exception as e:
    logger.error(f"Failed to map items to categories: {e}")
    raise

# Categories
tag_categories = {x: None for x in "main_tag spec_tag1 spec_tag2 spec_tag3 spec_tag4 spec_tag5 spec_tag6 semantic_tag1 semantic_tag2".split()}

# Index list
logger.info(f"Loading index list...")
try:
    index_list = open(f"{DATA_PATH}/lists_LGR/LGR_index_list_5-26-20.txt").read().split("\n")
    logger.info(f"Index list loaded.")
except Exception as e:
    logger.error(f"Failed to load index list: {e}")
    raise

@typechecked
def ex_tester(
        input_text: str
    ) -> None:
    """
    Example tester for checking spaCy output.\n
    ---
    ### Args
    - `input_text` (`str`): the text to test.
    """
    spcy_sample = nlp(input_text)
    for sent_number, sent in enumerate(spcy_sample.sents, 1):
        print(f"sent_number {sent_number}")
        for token in sent:
            print(token.text, token.lemma_, token.tag_, token.pos_, token.dep_, token.head.text, token.i)

@typechecked
def safe_divide(
        numerator,
        denominator
    ) -> float:
    """
    Safe division.\n
    ---
    ### Args
    - `numerator`
    - `denominator`
    """
    return 0.0 if float(denominator) == 0.0 else numerator / denominator

@typechecked
def prettify(
        element
    ) -> str:
    """
    Return a pretty-printed XML string for the Element.\n
    ---
    ### Args
    - `element`: the element to prettify
    """
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

@typechecked
def wrd_nchar(
        token,
        features: dict
    ) -> None:
    """
    Add word length and count to features.\n
    ---
    ### Args
    - `token`: the token.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ not in ["PUNCT", "SYM", "SPACE", "X"]:
        features["wrd_length"] += len(token.text)
        features["nwords"] += 1
        lemma = token.text.lower() if token.lemma_ == "-PRON-" else token.lemma_
        features["lemma_text"].append(f"{lemma}_{token.pos_}")

@typechecked
def noun_phrase_complexity(
        token,
        features: dict
    ) -> None:
    """
    Analyze noun phrase complexity.\n
    ---
    ### Args
    - `token`: the token.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ == "NOUN":
        features["np"] += 1
        deps = [child.dep_ for child in token.children]
        features["np_deps"] += len(deps)
        for x in deps:
            if x == "relcl": features["relcl_dep"] += 1
            if x == "amod": features["amod_dep"] += 1
            if x == "det": features["det_dep"] += 1
            if x == "prep": features["prep_dep"] += 1
            if x == "poss": features["poss_dep"] += 1
            if x == "cc": features["cc_dep"] += 1

@typechecked
def clausal_complexity(
        token,
        features: dict
    ) -> None:
    """
    Analyze clausal complexity.\n
    ---
    ### Args
    - `token`: the token.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ == "VERB" and token.dep_ != "aux":
        features["all_clauses"] += 1
        deps = [child.dep_ for child in token.children]
        if "nsubj" in deps or "nsubjpass" in deps:
            features["finite_clause"] += 1
            features["finite_ind_clause" if token.dep_ in ["ROOT", "conj"] else "finite_dep_clause"] += 1
            if token.dep_ == "ccomp": features["finite_compl_clause"] += 1
            if token.dep_ == "relcl": features["finite_relative_clause"] += 1
        else:
            features["nonfinite_clause"] += 1
        features["vp_deps"] += len(deps)

@typechecked
def basic_info(
        token,
        tokens: dict
    ) -> None:
    """
    Populate basic information for a token.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    """
    tokens.update({
        "word": token.text,
        "lemma": token.lemma_.lower(),
        "pos": token.pos_,
        "tag": token.tag_,
        "idx": str(token.i),
        "dep_rel": token.dep_,
        "head": token.head.text,
        "head idx": str(token.head.i)
    })

@typechecked
def pronoun_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze pronouns.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    pp1 = "i we our us my me ourselves myself".split()
    pp2 = "you your yourself ya thy thee thine".split()
    pp3 = "he she they their his them her him themselves himself herself".split()
    pp3_it = ["it"]
    pp_all = pp1 + pp2 + pp3 + pp3_it

    if token.text.lower() in pp_all:
        features["pp_all"] += 1
        tokens["main_tag"] = "pp_all"

    if token.text.lower() in pp1:
        features["pp1"] += 1
        tokens["spec_tag1"] = "pp1"
    elif token.text.lower() in pp2:
        features["pp2"] += 1
        tokens["spec_tag1"] = "pp2"
    elif token.text.lower() in pp3:
        features["pp3"] += 1
        tokens["spec_tag1"] = "pp3"
    elif token.text.lower() in pp3_it:
        features["pp3_it"] += 1
        tokens["spec_tag1"] = "pp3_it"

@typechecked
def advanced_pronoun(
        token,
        document,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze advanced pronouns.\n
    ---
    ### Args
    - `token`: the token.
    - `document`: the document.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    demonstrative_list = ["this", "that", "these", "those"]
    indefinite_l = "everybody everyone everything somebody someone something anybody anyone anything nobody noone none nothing one ones".split()

    if token.text.lower() in indefinite_l and token.dep_ in ["nsubj", "nsubjpass", "dobj", "pobj"]:
        features["pp_indefinite"] += 1
        tokens["spec_tag1"] = "pp_indefinite"
    elif token.text.lower() in demonstrative_list:
        if token.dep_ == "advmod" or (
            token.i + 1 < len(document) and document[token.i + 1].text.lower() in ["who", ".", "!", "?", ":"]
        ) or (
            token.dep_ == "nsubjpass" and token.head.dep_ != "relcl"
        ) or (
            token.dep_ == "pobj"
        ) or (
            token.dep_ in ["nsubj", "dobj"] and token.head.dep_ != "relcl" and token.head.pos_ != "NOUN"
        ):
            features["pp_demonstrative"] += 1
            tokens["spec_tag1"] = "pp_demonstrative"

@typechecked
def pro_verb(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze pro-verbs.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.lemma_ == "do" and token.pos_ == "VERB" and token.dep_ != "aux":
        if not any(child.dep_ in ["dobj", "ccomp"] for child in token.children):
            features["pv_do"] += 1
            tokens["spec_tag2"] = "pv_do"

@typechecked
def contraction_check(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Check for contractions.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.text.lower() in "'m 'll n't 're 's".split() and token.dep_ != "case":
        features["contraction"] += 1
        tokens["spec_tag4"] = "contraction"

@typechecked
def split_aux_check(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Check for split auxiliaries.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ == "VERB" and token.dep_ not in ["aux", "aux_pass"]:
        end = token.i
        start = next((x.i for x in token.children if x.dep_ in ["aux", "aux_pass"]), None)
        adv = next((x.i for x in token.children if x.dep_ == "advmod"), None)
        if start is not None and adv is not None and start < adv < end:
            features["split_aux"] += 1
            tokens["spec_tag2"] = "split_aux"

@typechecked
def prep_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze prepositions.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.dep_ == "mark":
        if token.text.lower() == "because":
            features["adverbial_subordinator_causitive"] += 1
            tokens["spec_tag3"] = "adverbial_subordinator_causitive"
        elif token.text.lower() in ["if", "unless"]:
            features["adverbial_subordinator_conditional"] += 1
            tokens["spec_tag3"] = "adverbial_subordinator_conditional"
        elif token.text.lower() not in ["that"]:
            features["adverbial_subordinator_other"] += 1
            tokens["spec_tag3"] = "adverbial_subordinator_other"
    elif token.dep_ == "prep":
        if any(child.dep_ in ["pobj", "pcomp", "prep", "amod", "cc"] for child in token.children):
            features["prep_phrase"] += 1
            tokens["main_tag"] = "prep_phrase"

@typechecked
def coordination_analysis(
        token,
        words_count: int,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze coordination.\n
    ---
    ### Args
    - `token`: the token.
    - `words_count` (`int`): the words count.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.text.lower() in ["and", "or"]:
        if words_count == 0:
            features["cc_clause"] += 1
            tokens["spec_tag1"] = "cc_clause"
        elif token.head.pos_ in ["NOUN", "ADJ", "ADV", "PRON", "PROPN", "PART"]:
            features["cc_phrase"] += 1
            tokens["spec_tag1"] = "cc_phrase"
        elif token.head.pos_ == "VERB":
            l = sorted(
                [(child.i, "cc_clause" if child.dep_ == "conj" and "nsubj" in [chld.dep_ for chld in child.children] else "cc_phrase") for child in token.head.children if child.dep_ in ["cc", "conj"]],
                key=lambda x: x[0]
            )
            for i, (idx, relation) in enumerate(l):
                if idx == token.i:
                    next_relation = l[i + 1][1] if i + 1 < len(l) else "cc_clause"
                    features[next_relation] += 1
                    tokens["spec_tag1"] = next_relation
                    break

@typechecked
def noun_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze nouns.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ in ["NOUN", "PROPN"]:
        features["nn_all"] += 1
        tokens["main_tag"] = "nn_all"
        nominal_suffixes = {
            6: ["nesses"],
            5: ["ician", "ities", "ances", "ences", "ments", "tions", "ships", "esses", "ettes", "hoods"],
            4: ["ance", "ence", "ment", "ness", "tion", "ship", "ette", "hood", "cies", "ries", "ants", "ents", "doms", "ings", "ages", "fuls", "isms", "ists", "ites", "lets", "eses", "ates"],
            3: ["ant", "ent", "dom", "ing", "ity", "ure", "age", "ese", "ess", "ful", "ism", "ist", "ite", "let", "als", "ees", "ers", "ors", "ate"],
            2: ["al", "cy", "ee", "er", "or", "ry"],
        }
        proper_suffixes = {
            4: ["ians"],
            3: ["ian", "ans"],
            2: ["an"],
        }
        if token.lemma_.lower() not in nominal_stop:
            for length, suffixes in nominal_suffixes.items():
                if len(token.text) > length and token.text.lower()[-length:] in suffixes:
                    features["nominalization"] += 1
                    tokens["spec_tag1"] = "nominalization"
                    break
            else:
                for length, suffixes in proper_suffixes.items():
                    if len(token.text) > length and token.pos_ == "PROPN" and token.text.lower()[-length:] in suffixes:
                        features["nominalization"] += 1
                        tokens["spec_tag1"] = "nominalization"
                        break

@typechecked
def semantic_analysis_noun(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze semantic tags for nouns.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ in ["NOUN", "PROPN"]:
        lemma = token.lemma_.lower()
        if lemma in noun_dict and noun_dict[lemma] in categories:
            features[noun_dict[lemma]] += 1
            tokens["semantic_tag1"] = noun_dict[lemma]

@typechecked
def be_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze `'be'` verbs.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.lemma_.lower() == "be" and token.dep_ not in ["aux", "auxpass"]:
        features["be_mv"] += 1
        tokens["spec_tag2"] = "be_mv"

@typechecked
def verb_analysis(
        token,
        document,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze verbs.\n
    ---
    ### Args
    - `token`: the token.
    - `document`: the document.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    that0_list = "check consider ensure illustrate fear say assume understand hold appreciate insist feel reveal indicate wish decide express follow suggest saw direct pray observe record imagine see think show confirm ask meant acknowledge recognize need accept contend come maintain believe claim verify demonstrate learn hope thought reflect deduce prove find deny wrote read repeat remember admit adds advise compute reach trust yield state describe realize expect mean report know stress note told held explain hear gather establish suppose found use fancy submit doubt felt".split()
    to_verb_list = "to_speech_act_verb cognition_verb desire_verb to_causative_verb probability_verb".split()
    to_adj_list = "certainty_adj ability_willingness_adj personal_affect_adj ease_difficulty_adj evaluative_adj".split()

    if token.pos_ == "VERB":
        features["verb"] += 1
        tokens["main_tag"] = "verb"
        if token.dep_ == "aux":
            if token.text in "can may might could".split():
                features["modal_possibility"] += 1
                tokens["spec_tag5"] = "modal_possibility"
            elif token.text in "ought must should".split():
                features["modal_necessity"] += 1
                tokens["spec_tag5"] = "modal_necessity"
            elif token.text in "will would shall".split():
                features["modal_predictive"] += 1
                tokens["spec_tag5"] = "modal_predictive"
            elif token.tag_ == "VBD":
                features["past_tense"] += 1
                tokens["spec_tag4"] = "past_tense"
            else:
                features["non_past_tense"] += 1
                tokens["spec_tag1"] = "non_past_tense"
        else:
            if token.head.lemma_ in that0_list and token.dep_ == "ccomp" and token.i > token.head.i:
                if all(
                    x.text.lower() not in ["that", "who", "what", "how", "where", "why", "when", "whose", "whom", "whomever"] and x.dep_ != "det"
                    for x in token.children
                ) and not any(
                    x.dep_ == "mark" or x.dep_ in ["nsubj", "csubj"] for x in token.children
                ) and token.tag_ != "VBG":
                    if document[token.head.i - 1].text not in ["that", "who", "what", "how", "where", "why", "when", "whose", "whom", "whomever", "whatever", "which"]:
                        if document[token.head.i + 1].text not in ["that", "who", "what", "how", "where", "why", "when", "whose", "whom", "whomever", "whatever", "which", '"', "'", ",", ":", "myself", "itself", "herself", "ourself", "ourselves", "themselves", "themself"]:
                            if " ".join([document[token.head.i + 1].text, document[token.head.i + 2].text]) not in ["' ,", '" ,']:
                                features["complementizer_that0"] += 1
                                tokens["spec_tag6"] = "complementizer_that0"
            if token.dep_ == "acl" and token.tag_ == "VBN":
                features["past_participial_clause"] += 1
                tokens["spec_tag6"] = "past_participial_clause"
            if document[token.i - 1].text.lower() == "to" and document[token.i - 1].dep_ == "aux" and document[token.i - 1].head.i == token.i:
                contr_token = document[token.i - 2]
                if contr_token.text.lower() not in ["able", "ought"]:
                    features["to_clause"] += 1
                    tokens["spec_tag4"] = "to_clause"
                    if contr_token.pos_ == "NOUN":
                        features["to_clause_noun"] += 1
                        tokens["spec_tag5"] = "to_clause_noun"
                    if contr_token.pos_ == "VERB":
                        features["to_clause_verb"] += 1
                        tokens["spec_tag5"] = "to_clause_verb"
                        if contr_token.lemma_ in to_verb_dict and to_verb_dict[contr_token.lemma_] in to_verb_list:
                            features[f"to_clause_verb_{to_verb_dict[contr_token.lemma_][:-5]}"] += 1
                            tokens["semantic_tag2"] = f"to_clause_verb_{to_verb_dict[contr_token.lemma_][:-5]}"
                    if contr_token.pos_ == "ADJ":
                        features["to_clause_adjective"] += 1
                        tokens["spec_tag5"] = "to_clause_adjective"
                        if contr_token.lemma_ in adj_dict and adj_dict[contr_token.lemma_] in to_adj_list:
                            features[f"to_clause_adjective_{adj_dict[contr_token.lemma_][:-4]}"] += 1
                            tokens["semantic_tag2"] = f"to_clause_adjective_{adj_dict[contr_token.lemma_][:-4]}"
            if token.tag_ == "VBD":
                features["past_tense"] += 1
                tokens["spec_tag1"] = "past_tense"
            elif token.tag_ in ["VBN", "VBG"]:
                if any(x.lemma_ == "have" and x.dep_ == "aux" for x in token.children):
                    features["perfect_aspect"] += 1
                    tokens["spec_tag1"] = "perfect_aspect"
            else:
                features["non_past_tense"] += 1
                tokens["spec_tag1"] = "non_past_tense"

@typechecked
def passive_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze passive voice.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.pos_ == "VERB" and any(x.dep_ == "auxpass" for x in token.children):
        if any(x.dep_ == "agent" for x in token.children):
            features["by_passive"] += 1
            tokens["spec_tag3"] = "by_passive"
        else:
            features["agentless_passive"] += 1
            tokens["spec_tag3"] = "agentless_passive"

@typechecked
def semantic_analysis_verb(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze semantic tags for verbs.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    var_list = "activity_verb communication_verb mental_verb causation_verb occurrence_verb existence_verb aspectual_verb that_nonfactive_verb attitudinal_verb factive_verb likelihood_verb".split()
    intransitive_phrasal_list = "intransitive_activity_phrasal_verb intransitive_occurence_phrasal_verb copular_phrasal_verb intransitive_aspectual_phrasal_verb".split()
    transitive_phrasal_list = "transitive_activity_phrasal_verb transitive_mental_phrasal_verb transitive_communication_phrasal_verb".split()

    lemma = token.lemma_.lower()
    if token.pos_ == "VERB":
        if "prt" in [chld.dep_ for chld in token.children]:
            for x in token.children:
                if x.dep_ == "prt":
                    phrasal = f"{lemma} {x.text}"
                    if phrasal in phrasal_verb_dict:
                        features["all_phrasal_verbs"] += 1
                        tokens["main_tag2"] = "all_phrasal_verbs"
                        if "dobj" in [chld.dep_ for chld in token.children]:
                            if phrasal in phrasal_verb_dict and phrasal_verb_dict[phrasal] in transitive_phrasal_list:
                                features[phrasal_verb_dict[phrasal]] += 1
                                tokens["semantic_tag1"] = phrasal_verb_dict[phrasal]
                        else:
                            if phrasal in phrasal_verb_dict and phrasal_verb_dict[phrasal] in intransitive_phrasal_list:
                                features[phrasal_verb_dict[phrasal]] += 1
                                tokens["semantic_tag1"] = phrasal_verb_dict[phrasal]
        else:
            if lemma in verb_dict and verb_dict[lemma] in var_list:
                features[verb_dict[lemma]] += 1
                tokens["semantic_tag1"] = verb_dict[lemma]

@typechecked
def adjective_analysis(
        token,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze adjectives.\n
    ---
    ### Args
    - `token`: the token.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    attr_list = "size_attributive_adj time_attributive_adj color_attributive_adj evaluative_attributive_adj relational_attributive_adj topical__attributive_adj".split()

    if token.dep_ in ["acomp"]:
        features["jj_predicative"] += 1
        tokens["spec_tag1"] = "jj_predicative"
        if token.lemma_.lower() in adj_dict and adj_dict[token.lemma_.lower()] in attr_list:
            features[adj_dict[token.lemma_.lower()]] += 1
            tokens["semantic_tag1"] = adj_dict[token.lemma_.lower()]
    elif token.dep_ == "amod":
        features["jj_attributive"] += 1
        tokens["spec_tag1"] = "jj_attributive"

@typechecked
def adverb_analysis(
        token,
        words_count: int,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze adverbs.\n
    ---
    ### Args
    - `token`: the token.
    - `words_count` (`int`): the words count.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    var_list = "discourse_particle place_adverbials time_adverbials conjuncts_adverb downtoners_adverb hedges_adverb amplifiers_adverb emphatics".split()
    var_list2 = "attitudinal_adverb factive_adverb likelihood_adverb nonfactive_adverb".split()

    lemma = token.lemma_.lower()
    if token.pos_ == "ADV" or token.dep_ in ["npadvmod", "advmod", "intj"]:
        if lemma in adv_dict and adv_dict[lemma] in var_list:
            features[adv_dict[lemma]] += 1
            tokens["spec_tag1"] = adv_dict[lemma]
        if words_count == 0 and token.text.lower() in "well now anyway anyhow anyways".split():
            features["discourse_particle"] += 1
            tokens["spec_tag1"] = "discourse_particle"
        elif lemma in adv_dict and adv_dict[lemma] in var_list2:
            features[adv_dict[lemma]] += 1
            tokens["semantic_tag1"] = adv_dict[lemma]

@typechecked
def wh_analysis(
        token,
        words_count,
        document,
        document_sentence,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze WH-words.\n
    ---
    ### Args
    - `token`: the token.
    - `words_count` (`int`): the words count.
    - `document`: the document.
    - `document_sentence`: the document sentence.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    if token.tag_ in ["WDT", "WP", "WP$", "WRB"] and token.text.lower() != "that":
        if token.head.dep_ not in ["csubj", "ccomp", "pcomp"] and (words_count == 0 or document[token.i - 1].text in ['"', "'", ":"]) and "?" in [t.text for t in document_sentence]:
            features["wh_question"] += 1
            tokens["spec_tag1"] = "wh_question"
        if document[token.i - 1].pos_ == "VERB" and document[token.i - 1].lemma_ != "be":
            if token.head.dep_ != "advcl":
                features["wh_clause"] += 1
                tokens["spec_tag1"] = "wh_clause"
        if token.dep_ == "pobj" and token.head.head.dep_ == "relcl":
            features["wh_relative_clause"] += 1
            tokens["main_tag"] = "wh_relative_clause"
            features["wh_relative_prep_clause"] += 1
            tokens["spec_tag1"] = "wh_relative_prep_clause"
        if token.head.dep_ == "relcl":
            if token.dep_ in ["nsubj", "nsubjpass"]:
                features["wh_relative_clause"] += 1
                tokens["main_tag"] = "wh_relative_clause"
                features["wh_relative_subj_clause"] += 1
                tokens["spec_tag1"] = "wh_relative_subj_clause"
            if token.dep_ in ["dobj"]:
                features["wh_relative_clause"] += 1
                tokens["main_tag"] = "wh_relative_clause"
                features["wh_relative_obj_clause"] += 1
                tokens["spec_tag1"] = "wh_relative_obj_clause"

@typechecked
def that_analysis(
        token,
        document,
        tokens: dict,
        features: dict
    ) -> None:
    """
    Analyze `'that'` clauses.\n
    ---
    ### Args
    - `token`: the token.
    - `document`: the document.
    - `tokens` (`dict`): the tokens dictionary.
    - `features` (`dict`): the features dictionary.
    """
    that_verb_list = "nonfactive_verb attitudinal_verb factive_verb likelihood_verb".split()
    that_noun_list = "nn_nonfactive nn_attitudinal nn_factive_noun nn_likelihood".split()

    if token.text.lower() == "that":
        if token.dep_ in ["nsubj", "nsubjpass", "dobj", "pobj"] and token.head.dep_ == "relcl":
            features["that_relative_clause"] += 1
            tokens["spec_tag1"] = "that_relative_clause"
        if token.dep_ in ["mark", "nsubj"] and token.head.dep_ in ["ccomp", "acl"]:
            features["that_complement_clause"] += 1
            tokens["spec_tag1"] = "that_complement_clause"
            if document[token.i - 1].pos_ == "VERB":
                features["that_verb_clause"] += 1
                tokens["spec_tag2"] = "that_verb_clause"
                verb_lemma = document[token.i - 1].lemma_.lower()
                if verb_lemma in that_verb_dict and that_verb_dict[verb_lemma] in that_verb_list:
                    features[f"that_verb_clause_{that_verb_dict[verb_lemma][:-5]}"] += 1
                    tokens["semantic_tag1"] = f"that_verb_clause_{that_verb_dict[verb_lemma][:-5]}"
            if document[token.i - 1].pos_ == "NOUN":
                features["that_noun_clause"] += 1
                tokens["spec_tag2"] = "that_noun_clause"
                noun_lemma = document[token.i - 1].lemma_.lower()
                if noun_lemma in noun_dict and noun_dict[noun_lemma] in that_noun_list:
                    features[f"that_noun_clause_{noun_dict[noun_lemma][3:]}"] += 1
                    tokens["semantic_tag1"] = f"that_noun_clause_{noun_dict[noun_lemma][3:]}"
            if document[token.i - 1].pos_ == "ADJ":
                features["that_adjective_clause"] += 1
                tokens["spec_tag2"] = "that_adjective_clause"
                adj_lemma = document[token.i - 1].lemma_.lower()
                if adj_lemma in adj_dict:
                    if adj_dict[adj_lemma] == "attitudinal_adj":
                        features["that_adjective_clause_attitudinal"] += 1
                        tokens["semantic_tag1"] = "that_adjective_clause_attitudinal"
                    if adj_dict[adj_lemma] == "likelihood_adj":
                        features["that_adjective_clause_likelihood"] += 1
                        tokens["semantic_tag1"] = "that_adjective_clause_likelihood"

@typechecked
def LGR_Analysis(
        text,
        indices_dict: List[str] = index_list,
        tag_categories_d: dict = tag_categories,
        output: bool = False
    ) -> Any:
    logger.debug(f"Analyzing text: {text[:100]}...")  # Log first 100 characters for brevity
    index_dict = {x: 0 for x in indices_dict}
    index_dict["lemma_text"] = []

    def clean_text(in_text):
        in_text = re.sub(r"\[.*?\]", "", in_text)
        in_text = re.sub(r"\n[0-9]:", "", in_text)
        if " " in in_text:
            if "\n" not in in_text:
                in_text = " ".join(in_text.split())
            else:
                in_text = "\n".join(" ".join(x.split()) for x in in_text.split("\n"))
        return in_text

    document = nlp(clean_text(text))
    logger.debug(f"Document processed: {document}")

    output_list = []
    for sent_idx, sent in enumerate(document.sents):
        output_list.append([])
        for idx_sent, token in enumerate(sent):
            token_attrs = {x: None for x in tag_categories_d}
            basic_info(token, token_attrs)
            pronoun_analysis(token, token_attrs, index_dict)
            advanced_pronoun(token, document, token_attrs, index_dict)
            pro_verb(token, token_attrs, index_dict)
            contraction_check(token, token_attrs, index_dict)
            split_aux_check(token, token_attrs, index_dict)
            prep_analysis(token, token_attrs, index_dict)
            coordination_analysis(token, idx_sent, token_attrs, index_dict)
            wh_analysis(token, idx_sent, document, sent, token_attrs, index_dict)
            noun_analysis(token, token_attrs, index_dict)
            semantic_analysis_noun(token, token_attrs, index_dict)
            be_analysis(token, token_attrs, index_dict)
            verb_analysis(token, document, token_attrs, index_dict)
            passive_analysis(token, token_attrs, index_dict)
            semantic_analysis_verb(token, token_attrs, index_dict)
            adjective_analysis(token, token_attrs, index_dict)
            adverb_analysis(token, idx_sent, token_attrs, index_dict)
            that_analysis(token, document, token_attrs, index_dict)
            wrd_nchar(token, index_dict)
            noun_phrase_complexity(token, index_dict)
            clausal_complexity(token, index_dict)
            output_list[sent_idx].append(token_attrs)

    index_dict["tagged_text"] = output_list
    index_dict["wrd_length"] = index_dict["wrd_length"] / index_dict["nwords"]
    index_dict["mattr"] = ld.mattr(index_dict["lemma_text"])

    # noun phrase complexity
    index_dict.update({
        "mean_nominal_deps": safe_divide(index_dict["np_deps"], index_dict["np"]),
        "relcl_nominal": safe_divide(index_dict["relcl_dep"], index_dict["np"]),
        "amod_nominal": safe_divide(index_dict["amod_dep"], index_dict["np"]),
        "det_nominal": safe_divide(index_dict["det_dep"], index_dict["np"]),
        "prep_nominal": safe_divide(index_dict["prep_dep"], index_dict["np"]),
        "poss_nominal": safe_divide(index_dict["poss_dep"], index_dict["np"]),
        "cc_nominal": safe_divide(index_dict["cc_dep"], index_dict["np"]),
        "mean_verbal_deps": safe_divide(index_dict["vp_deps"], index_dict["finite_clause"]),
        "mlc": safe_divide(index_dict["nwords"], index_dict["finite_clause"]),
        "mltu": safe_divide(index_dict["nwords"], index_dict["finite_ind_clause"]),
        "dc_c": safe_divide(index_dict["finite_dep_clause"], index_dict["finite_clause"]),
        "ccomp_c": safe_divide(index_dict["finite_compl_clause"], index_dict["finite_clause"]),
        "relcl_c": safe_divide(index_dict["finite_relative_clause"], index_dict["finite_clause"]),
        "infinitive_prop": safe_divide(index_dict["to_clause"], index_dict["all_clauses"]),
        "nonfinite_prop": safe_divide(index_dict["nonfinite_clause"], index_dict["all_clauses"])
    })

    return index_dict

@typechecked
def output_vertical(
        list_text,
        outname,
        ordered_output = "simple",
        pretty_print: bool = False
    ) -> None:
    """
    Output parsed text to vertical format.
    """
    ordered_output = {
        "full": ['idx', 'word', 'lemma', 'pos', 'tag', 'dep_rel', 'head', 'head idx', 'main_tag', 'spec_tag1', 'spec_tag2', 'spec_tag3', 'spec_tag4', 'spec_tag5', 'spec_tag6', 'semantic_tag1', 'semantic_tag2'],
        "simple": ['idx', 'word', 'lemma', 'tag', 'dep_rel', 'head idx', 'main_tag', 'spec_tag1', 'spec_tag2', 'spec_tag3', 'spec_tag4', 'spec_tag5', 'spec_tag6', 'semantic_tag1', 'semantic_tag2']
    }[ordered_output]

    with open(outname, "w") as outf:
        for sent_id, sent in enumerate(list_text):
            if not sent:
                continue
            outf.write(f"\n\n[Sentence {sent_id}]")
            if pretty_print:
                print("\n\n")
            for token in sent:
                out_list = [str(token.get(attr, "n/a")) for attr in ordered_output]
                outf.write("\n" + "\t".join(out_list))
                if pretty_print:
                    print("\n" + "\t".join(out_list))

@typechecked
def print_vertical(
        list_text,
        ordered_output = "simple"
    ) -> None:
    """
    Print parsed text in vertical format.
    """
    ordered_output = {
        "full": ['idx', 'word', 'lemma', 'pos', 'tag', 'dep_rel', 'head', 'head idx', 'main_tag', 'spec_tag1', 'spec_tag2', 'spec_tag3', 'spec_tag4', 'spec_tag5', 'spec_tag6', 'semantic_tag1', 'semantic_tag2'],
        "simple": ['idx', 'word', 'lemma', 'tag', 'dep_rel', 'head idx', 'main_tag', 'spec_tag1', 'spec_tag2', 'spec_tag3', 'spec_tag4', 'spec_tag5', 'spec_tag6', 'semantic_tag1', 'semantic_tag2']
    }[ordered_output]

    for sent_id, sent in enumerate(list_text):
        if not sent: continue
        print(f"\n\n[Sentence {sent_id}]")
        for token in sent:
            out_list = [str(token.get(attr, "n/a")) for attr in ordered_output]
            print("\n" + "\t".join(out_list))

@typechecked
def output_xml(
        list_text,
        outname = False,
        xml_element = None
    ) -> Union[Any, ET.Element, None]:
    """
    Output parsed text to XML format.
    """
    LGR_attr_list = ['main_tag', 'spec_tag1', 'spec_tag2', 'spec_tag3', 'spec_tag4', 'spec_tag5', 'spec_tag6', 'semantic_tag1', 'semantic_tag2']
    xml_element = xml_element or ET.Element("tagged_text")

    for sent_id, sent in enumerate(list_text):
        sent_level = ET.SubElement(xml_element, "sentence", attrib={"sent_id": str(sent_id)})
        sent_text = ET.SubElement(sent_level, "sentence_text")
        sentence_list = []

        for item in sent:
            sentence_list.append(item["word"])
            wrd = ET.SubElement(sent_level, "word", attrib={"idx": item["idx"]})
            ET.SubElement(wrd, "raw").text = item["word"]
            ET.SubElement(wrd, "lemma").text = item["lemma"]
            btt = ET.SubElement(wrd, "biber_tags")
            for x in LGR_attr_list:
                if item[x]:
                    btt.set(x, item[x])
            ET.SubElement(wrd, "UPOS").text = item["pos"]
            ET.SubElement(wrd, "POS").text = item["tag"]
            head_rel = ET.SubElement(wrd, "DEP")
            head_rel.text = item["dep_rel"]
            head_rel.set("head", item["head"])
            head_rel.set("head_id", str(item["head idx"]))

        sent_text.text = " ".join(sentence_list)

    if outname:
        with open(outname, "w") as outf:
            outf.write(prettify(xml_element))
    else:
        return xml_element

@typechecked
def sent_exampler(
        list_text,
        target
    ) -> list:
    """
    Find and return sentences containing the target tag.
    """
    outl = []
    for sent in list_text:
        if not sent: continue
        s_text = []
        keep_s = False
        for token in sent:
            s_text.append(token["word"])
            if target in token.values():
                keep_s = True
                s_text.append(f"<--{target}<<<")
        if keep_s:
            outl.append(" ".join(s_text))
    return outl

@typechecked
def LGR_Full(
        filenames,
        outname,
        indices_dict: List[str] = index_list,
        tag_categories_d: Dict[str, None] = tag_categories,
        outdirname: str = '',
        output = None
    ) -> None:
    noNorm = ["nwords", "wrd_length", "mean_nominal_deps", "relcl_nominal", "amod_nominal", "det_nominal", "prep_nominal", "poss_nominal", "cc_nominal", "mean_verbal_deps", "mlc", "mltu", "dc_c", "ccomp_c", "relcl_c", "infinitive_prop", "nonfinite_prop"]
    with open(outname, "w") as outf:
        outf.write("filename," + ",".join(indices_dict))
        if output:
            if "xml" in output and not os.path.exists(outdirname + "/xml/"):
                os.mkdir(outdirname + "/xml/")
            if "vertical" in output and not os.path.exists(outdirname + "/vertical/"):
                os.mkdir(outdirname + "/vertical/")
        filenames = glob.glob(filenames + "*.txt") if type(filenames) == str else filenames

        for filename in filenames:
            simple_fname = os.path.basename(filename)
            text = open(filename).read()
            tag_output = LGR_Analysis(text, indices_dict, tag_categories_d)
            output_list = [simple_fname] + [
                str(tag_output[x]) if x in noNorm else str((tag_output[x] / tag_output["nwords"]) * 10000)
                for x in indices_dict
            ]
            logger.debug(f"Writing to CSV: {output_list}")
            outf.write("\n" + ",".join(output_list))
            if output:
                if "xml" in output:
                    output_xml(tag_output["tagged_text"], outdirname + "/xml/" + os.path.splitext(simple_fname)[0] + ".xml")
                    logger.info(f"Generated file '{simple_fname.replace('txt', 'xml')}'.")
                if "vertical" in output:
                    output_vertical(tag_output["tagged_text"], outdirname + "/vertical/" + os.path.splitext(simple_fname)[0] + ".tsv", ordered_output="full")
                    logger.info(f"Generated file '{simple_fname.replace('txt', 'tsv')}'.")


@typechecked
def calcFromXml(
        xml_filename,
        indices_dict: List[str] = index_list
    ) -> Dict[str, int]:
    """
    Calculate counts from XML files.
    """
    simplefilename = os.path.basename(xml_filename)
    index_dict = {x: 0 for x in indices_dict}
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    for tags in root.iter("biber_tags"):
        for x in tags.attrib:
            feature = tags.attrib[x]
            if feature in index_dict:
                index_dict[feature] += 1
            else:
                logger.warning(f"The tag '{feature}' is not a recognized tag. Please double check the file '{simplefilename}'.")

    for upos in root.iter("UPOS"):
        if upos.text not in ["PUNCT", "SYM", "SPACE", "X"]:
            index_dict["nwords"] += 1

    return index_dict

@typechecked
def lgrXml(
        filenames,
        outname,
        indices_dict: List[str] = index_list
    ) -> None:
    """
    LGR XML analysis.
    """
    logger.info(f"Outname: '{outname}'")
    with open(outname, "w") as outf:
        index_list = [x for x in indices_dict if x not in ["wrd_length", "mattr", "np", "np_deps", "relcl_dep", "amod_dep", "det_dep", "prep_dep", "poss_dep", "cc_dep", "all_clauses", "finite_clause", "finite_ind_clause", "finite_dep_clause", "finite_compl_clause", "finite_relative_clause", "nonfinite_clause", "vp_deps"]]
        outf.write("filename," + ",".join(index_list))
        for filename in filenames:
            tagDict = calcFromXml(filename, index_list)
            simple_fname = os.path.basename(filename)
            logger.info(f"Generated file '{simple_fname}'.")
            output_list = [simple_fname] + [
                str(tagDict[x]) if x in ["nwords", "wrd_length"] else str((tagDict[x] / tagDict["nwords"]) * 10000)
                for x in index_list
            ]
            outf.write("\n" + ",".join(output_list))

@typechecked
def LGR_XML(
        xml_files,
        outname,
        index_list: List[str],
        tag_categories: dict):
    """
    LGR XML analysis for TMLE xml texts.
    """
    with open(outname, "w") as outf:
        ignore_list = ["np", "np_deps", "relcl_dep", "amod_dep", "det_dep", "prep_dep", "poss_dep", "cc_dep", "all_clauses", "finite_clause", "finite_ind_clause", "finite_dep_clause", "finite_compl_clause", "finite_relative_clause", "nonfinite_clause", "vp_deps"]
        refined_index_list = [x for x in index_list if x not in ignore_list]
        outf.write("filename,learning_environment,mode,discipline,subdiscipline,text_type," + ",".join(refined_index_list))

        tt_list = open(f"{DATA_PATH}/lists_LGR/text_type_map_2020-5-24.txt").read().split("\n")
        tt_dict = {x.split("\t")[0] + "\t" + x.split("\t")[1] + "\t" + x.split("\t")[2]: x.split("\t")[3] for x in tt_list}

        def discipline_fixer(discipline: str):
            typo_dict = {"natural_sciences": "natural_science", "natual_science": "natural_science", "anthropology": "humanities", "social_sciences": "social_science", "marketing": "business", "astronomy": "natural_science", "english": "humanities", "chemistry": "natural_science", "pnatural_science": "natural_science", "n/a": "service_encounters"}
            return typo_dict.get(discipline.lower().split(" ")[0], discipline.lower())

        def cleaner(thingy: str):
            return thingy.replace(",", "_").replace(" ", "_")

        for filename in xml_files:
            simple_fname = os.path.basename(filename)
            logger.info(f"Generated file '{simple_fname}'.")
            tree = ET.parse(filename)
            root = tree.getroot()
            le = root[0].attrib.get("learning_environment", "tmle")
            if le != "traditional" and root[0].attrib["provided_by"] == "student":
                continue

            sdp = cleaner(root[0].attrib.get("subdiscipline", root[0].attrib.get("subject", "n/a")))
            pre_tt = f"{le}\t{root[0].attrib['mode']}\t{cleaner(root[0].attrib['file_type'])}"
            output_list = [simple_fname, le, root[0].attrib["mode"], discipline_fixer(root[0].attrib["discipline"]), sdp, tt_dict[pre_tt]]

            text = root[2].text if root[1].attrib["text_type"] not in ["plain_text", "plaintext"] and len(root) > 2 else root[1].text
            output = LGR_Analysis(text, index_list, tag_categories)
            no_norming = ["nwords", "wrd_length", "mattr", "mean_nominal_deps", "relcl_nominal", "amod_nominal", "det_nominal", "prep_nominal", "poss_nominal", "cc_nominal", "mean_verbal_deps", "mlc", "mltu", "dc_c", "ccomp_c", "relcl_c", "infinitive_prop", "nonfinite_prop"]
            output_list += [str(output[x]) if x in no_norming else str((output[x] / output["nwords"]) * 10000) for x in refined_index_list]
            outf.write("\n" + ",".join(output_list))

@typechecked
def Simple_XML_Reader(
        xml_files,
        index_list: List[str],
        tag_categories: dict,
        target
    ) -> list:
    """
    Find and return example sentences containing the target tag.
    """
    ex_sents = []
    for filename in xml_files:
        simple_fname = os.path.basename(filename)
        logger.info(f"Generated file '{simple_fname}'.")
        tree = ET.parse(filename)
        root = tree.getroot()
        text = root[2].text if root[1].attrib["text_type"] not in ["plain_text", "plaintext"] and len(root) > 2 else root[1].text
        ex_sents += sent_exampler(LGR_Analysis(text, index_list, tag_categories, output=True)["tagged_text"], target)
    return ex_sents

@typechecked
def LGR_tt_find(xml_files) -> None:
    """
    Find text types.
    """
    tt_list = open(f"{DATA_PATH}/lists_LGR/text_type_map.txt").read().split("\n")
    tt_dict = {x.split("\t")[0]: x.split("\t")[1] for x in tt_list}

    def cleaner(thingy:str):
        return thingy.replace(",", "_").replace(" ", "_")

    for filename in xml_files:
        simple_fname = os.path.basename(filename)
        tree = ET.parse(filename)
        root = tree.getroot()
        file_type = cleaner(root[0].attrib["file_type"])
        if file_type not in tt_dict:
            logger.info(f"File type: '{file_type}'")

@typechecked
def LGR_discipline_check(xml_files) -> dict:
    """
    Check disciplines.
    """
    def discipline_fixer(discipline:str):
        dp = discipline.lower().split(" ")[0]
        if dp == "social":
            return "social_science"
        elif dp == "natural":
            return "natural_science"
        return dp

    discipline_dict = {}
    for filename in xml_files:
        simple_fname = os.path.basename(filename)
        tree = ET.parse(filename)
        root = tree.getroot()
        discipline = discipline_fixer(root[0].attrib["discipline"])
        discipline_dict[discipline] = discipline_dict.get(discipline, 0) + 1
    return discipline_dict

@typechecked
def clean_text(in_text:str) -> str:
    """
    Clean input text.
    """
    in_text = re.sub(r"\[.*?\]", "", in_text)
    in_text = re.sub(r"\n[0-9]:", "", in_text)
    if " " in in_text:
        if "\n" not in in_text:
            in_text = " ".join(in_text.split())
        else:
            in_text = "\n".join(" ".join(x.split()) for x in in_text.split("\n"))
    return in_text