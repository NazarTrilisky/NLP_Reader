import spacy
nlp = spacy.load('en_core_web_sm')   # sm md lg
import pdb
from difflib import SequenceMatcher

# find answers and show them


class Compare:
    """
    Container for how relevancy is determined
    and how potential answers are highlighted
    """
    def __init__(self):
        self.relevancy_method_redirect = relevancy_default
        self.highlight_method_redirect = highlight_default
        self.qdict = {}  # key = token.dep_, value = token for question

    def relevancy_method(self, question, sentence):
        return self.relevancy_method_redirect(question, sentence, self.qdict)

    def highlight_method(self, sentence):
        return self.highlight_method_redirect(sentence)


def relevancy_default(question, sentence, qdict):
    """
    Return the overall similarity score for the question and sentence
    arg: question: Spacy tokens doc of the question asked
    arg: sentence: Spacy tokens doc of the sentence evaluated
    arg: qdict: question dictionary with key = token.dep_, value = token
    return: float 0 to 1, 1 being the most similar
    """
    return question.similarity(sentence)


def relevancy_numeric(question, sentence, qdict):
    """
    If sentences has 1+ numeric tokens then return relevancy_default
      otherwise return 0
    arg: question: Spacy tokens doc of the question asked
    arg: sentence: Spacy tokens doc of the sentence evaluated
    arg: qdict: dictionary with key = token.dep_ and value = token
      e.g. {u'nsubj', token_obj, ...}
      subset of the information in 'question', but arranged as a dict
    return: float 0 to infinity, infinity being the most similar
    """
    numeric_deps = [u'amod', u'advmod']
    dep_weights = {u'nsubj': 2, u'dobj': 4, u'ROOT': 2}
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    score = get_score(sentence, qdict, dep_weights)
    for token in sentence:
        if not token.is_stop:
            if token.dep_ in numeric_deps or token.pos_ == u'NUM':
                score += .5
    return score


def relevancy_location(question, sentence, qdict):
    loc_ent_types = [u'GPE', u'LOC']  # entity types for locations
    dep_weights = {u'nsubj': 4, u'dobj': 2, u'ROOT': 4}
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    score = get_score(sentence, qdict, dep_weights) 
    for token in sentence:
        if not token.is_stop:
            if token.ent_type_ in loc_ent_types:
                score += .5
    return score


def relevancy_time(question, sentence, qdict):
    time_ent_types = [u'TIME', u'DATE', u'EVENT']  # entity types for times / events
    dep_weights = {u'nsubj': 4, u'ROOT': 4}
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    score = get_score(sentence, qdict, dep_weights)
    for token in sentence:
        if not token.is_stop:
            if token.ent_type_ in time_ent_types:
                score += .5
    return score


def relevancy_who(question, sentence, qdict):
    time_ent_types = [u'PERSON']
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    if 'whom' in qlemmas:
        dep_weights = {u'nsubj': 4, u'ROOT': 4}
    elif 'who' in qlemmas:
        dep_weights = {u'dobj': 4, u'ROOT': 4}
    else:
        raise Exception("Relevancy_who called, but no 'who' or 'whom' in question!")

    score = get_score(sentence, qdict, dep_weights)
    for token in sentence:
        if not token.is_stop:
            if token.ent_type_ in time_ent_types:
                score += .5
    return score


def relevancy_what_which(question, sentence, qdict):
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    if 'what' in qlemmas:
        dep_weights = {u'nsubj': 4, u'ROOT': 4, u'pobj': 2, u'attr': 3}
    elif 'which' in qlemmas:
        dep_weights = {u'nsubj': 4, u'ROOT': 4, u'dobj': 4, u'acomp': 3,
                       u'pobj': 2, u'advmod': 2, u'attr': 3}
    else:
        msg = "Relevancy_what_which called, but no 'what' or 'which' in question!"
        raise Exception(msg)
    return get_score(sentence, qdict, dep_weights)


def get_score(sentence, qdict, dep_weights):
    score = 0
    num_lemma_matches = 0  # how many question words matched sentence words
    LEMMA_MATCH_POINTS = 8  # points for each lemma match
    LEMMA_MATCH_GROWTH = 1.7  # rate of growth for multiple lemma matches
    LEMMA_MATCH_CUTOFF = 0.8  # lemma similarity to be considered identical
    for token in sentence:
        if not token.is_stop:
            # if question's main dep_ lemma_ is in sentence
            for qtoken in qdict.values():
                # semantic similarity
                qsimilarity = token.similarity(qtoken)
                if qtoken.dep_ in dep_weights.keys():
                    qsimilarity *= dep_weights[qtoken.dep_]
                # word root matching
                ratio = SequenceMatcher(None, qtoken.lemma_, token.lemma_).ratio()
                if ratio >= LEMMA_MATCH_CUTOFF:
                    num_lemma_matches += 1
                score += qsimilarity
    sum_lemma_match_points = num_lemma_matches * LEMMA_MATCH_POINTS
    score += sum_lemma_match_points * (LEMMA_MATCH_GROWTH ** num_lemma_matches)
    return score


def relevancy_why_how(question, sentence, qdict):
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    if 'why' in qlemmas:
        dep_weights = {u'nsubj': 4, u'ROOT': 4, u'dobj': 4, u'pobj': 1,
                       u'advmod': 2, u'xcomp': 1}
    elif 'how' in qlemmas:
        dep_weights = {u'nsubj': 4, u'ROOT': 4, u'dobj': 3, u'xcomp': 1, u'acomp': 1}
    else:
        raise Exception("Relevancy_why_how called, but no 'why' or 'how' in question!")
    return get_score(sentence, qdict, dep_weights)


def relevancy_choice(question, sentence, qdict):
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    dep_weights = {u'nsubj': 4, u'ROOT': 4, u'conj': 3, u'acomp': 3, u'amod': 2,
                   u'dobj': 2, u'npadvmod': 2}
    return get_score(sentence, qdict, dep_weights)


def relevancy_yes_no(question, sentence, qdict):
    qlemmas = [qtuple.lemma_ for qtuple in qdict.values()]
    dep_weights = {u'nsubj': 4, u'ROOT': 4, u'conj': 3, u'acomp': 3, u'amod': 2,
                   u'dobj': 2, u'npadvmod': 2, 'advmod': 3}
    return get_score(sentence, qdict, dep_weights)


def highlight_choice(sent):
    key_deps = [u'nsubj', u'dobj', u'attr', u'pobj']
    return get_highlighted(sent, key_deps)
    

def highlight_yes_no(sent):
    key_deps = [u'nsubj', u'dobj', u'attr', u'pobj']
    return get_highlighted(sent, key_deps)


def highlight_why_how(sent):
    key_deps = [u'nsubj', u'dobj', u'ROOT']
    return get_highlighted(sent, key_deps)


def highlight_what_which(sent):
    key_deps = [u'nsubj', u'dobj', u'ROOT']
    return get_highlighted(sent, key_deps)


def highlight_who(sent):
    key_deps = [u'nsubj', u'dobj']
    return get_highlighted(sent, key_deps)


def get_highlighted(sent, deps):
    """
    arg: sent: Spacy document
    arg: deps: list of unicode strings of depenency
      names to highlight, e.g. [u'nsubj', u'ROOT', ...]
    return: tuple as ([list of answer words], sent_new)
      sent_new is sent with the answer words highlighted
    """
    new_sent = ''
    ans_words = []
    for token in sent:
        if token.dep_ in deps:
            new_sent += token.text.upper() + ' '
            ans_words.append(token.text)
        else:
            new_sent += token.text + ' '
    return (ans_words, new_sent)


def highlight_time(sent):
    key_deps = [u'pobj', u'prep', u'npadvmod', u'advmod', u'advcl']
    return get_highlighted(sent, key_deps)


def highlight_location(sent):
    key_deps = [u'pobj', u'prep']
    return get_highlighted(sent, key_deps)


def highlight_default(sent):
    """
    arg: sent: string with potential answers to highlight
    return: tuple as ([list of answer words], sent_new)
      sent_new is sent with the answer words highlighted
    """
    return ([], sent.text)


def highlight_numeric(sent):
    new_sent = ''
    ans_words = []
    for token in sent:
        if token.pos_ == u'NUM' or token.dep_ == u'nummod':
            new_sent += token.text.upper() + ' '
            ans_words.append(token.text)
        else:
            new_sent += token.text + ' '
    return (ans_words, new_sent)




