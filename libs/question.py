# interpret the question
# setup comparison and relevancy based on the question

import re
import relevancy
import pdb


def define_comparison(question):
    """
    Get a search strategy for the given question
    arg: question: Spacy tokens doc
    return: Compare instance
    """
    comp_obj = relevancy.Compare()
    comp_obj.qdict = get_qdict_general(question)
    max_indx = len(question) - 1

    # yes/no question or choice question
    if question and (question[0].dep_ == u'aux' or question[0].dep_ == u'ROOT'):
        is_or = False
        for token in question[1:]:
            if token.lemma_ == u'or' and token.dep_ == u'cc':
                is_or = True
        if is_or:
            print("----- using choice similarity and highlighting")
            comp_obj.relevancy_method_redirect = relevancy.relevancy_choice
            comp_obj.highlight_method_redirect = relevancy.highlight_choice
        else:
            print("----- using yes/no similarity and highlighting")
            comp_obj.relevancy_method_redirect = relevancy.relevancy_yes_no
            comp_obj.highlight_method_redirect = relevancy.highlight_yes_no
        
    else:  # not yes/no or choice question
        for indx in range(len(question)):
            # if question seeks numeric answer
            # e.g. how much, how often, how quickly, ...
            numeric_deps = [u'amod', u'advmod']
            if 'how' == question[indx].lemma_:
                if indx <= max_indx:
                    next_token = question[indx + 1]
                    if next_token.dep_ in numeric_deps or token.pos_ == u'NUM':
                        print("----- using numeric similarity and highlighting")
                        comp_obj.relevancy_method_redirect = relevancy.relevancy_numeric
                        comp_obj.highlight_method_redirect = relevancy.highlight_numeric
                        break

            # if question seeks location answer
            elif 'where' == question[indx].lemma_:
                print("------ using location similarity and highlighting")
                comp_obj.relevancy_method_redirect = relevancy.relevancy_location
                comp_obj.highlight_method_redirect = relevancy.highlight_location
                break

            # if question seeks chronological answer
            elif 'when' == question[indx].lemma_:
                print("------ using time similarity and highlighting")
                comp_obj.relevancy_method_redirect = relevancy.relevancy_time
                comp_obj.highlight_method_redirect = relevancy.highlight_time
                break

            # if question seeks who(m) answer
            elif 'who' == question[indx].lemma_ or 'whom' == question[indx].lemma_:
                print("------ using who(m) similarity and highlighting")
                comp_obj.relevancy_method_redirect = relevancy.relevancy_who
                comp_obj.highlight_method_redirect = relevancy.highlight_who
                break

            # if question seeks what/which answer
            elif 'what' == question[indx].lemma_ or 'which' == question[indx].lemma_:
                print("------ using what/which similarity and highlighting")
                comp_obj.relevancy_method_redirect = relevancy.relevancy_what_which
                comp_obj.highlight_method_redirect = relevancy.highlight_what_which
                break

            # if question seeks why/how answer
            elif 'why' == question[indx].lemma_ or 'how' == question[indx].lemma_:
                print("------ using why/how similarity and highlighting")
                comp_obj.relevancy_method_redirect = relevancy.relevancy_why_how
                comp_obj.highlight_method_redirect = relevancy.highlight_why_how
                break

    return comp_obj


def get_qdict_general(question):
    """
    Get the question tokens' data as a dictionary
    arg: question: Spacy tokens doc of question asked
    return: dictionary with key = token.dep_ and value = token
      e.g. {u'nsubj': 'Beauty', u'dobj': 'Beast', u'ROOT': 'scare', ...}
    """
    dct = {}
    for token in question:
        if token.dep_ not in dct.keys():
            dct[token.dep_] = token
    return dct

