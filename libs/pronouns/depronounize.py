import spacy
from collections import deque

from pronouns_gender_number import \
  PLURAL_PRONOUNS, SINGULAR_PRONOUNS,\
  MASCULINE_PRONOUNS, FEMININE_PRONOUNS

from masculine import masculine  # list of masculine nouns/names lower-case
from feminine import feminine  # list of feminine nouns/names lower-case


nlp = spacy.load('en_core_web_sm')  # md / sm


# nouns that will be treated as pronouns
NOUNS_AS_PRONOUNS = ['who', 'that']


def update_last(deque_obj, new_value):
    deque_obj.rotate(-1)
    deque_obj[-1] = new_value


def is_masculine(token):
    if token.text.lower() in masculine:
        return True
    #if token.lemma_.lower() in masculine:
    #    return True
    return False


def is_feminine(token):
    if token.text.lower() in feminine:
        return True
    #if token.lemma_.lower() in feminine:
    #    return True
    return False


def match_last_pronoun(nouns, pronoun):
    """
    Starting from the end of the 'noun' deque, find the first
      noun that matches in gender and number
    arg: nouns: dequeue of five last-mentioned noun tokens
    arg: pronoun: pronoun token to replace with a noun
    return: latest matching noun token or None if no matches
    """
    pron_is_plur = pronoun.text.lower() in PLURAL_PRONOUNS
    pron_is_sing = pronoun.text.lower() in SINGULAR_PRONOUNS
    pron_is_masc = pronoun.text.lower() in MASCULINE_PRONOUNS
    pron_is_fem = pronoun.text.lower() in FEMININE_PRONOUNS

    #print("matching pronoun: >>%s<< against %s" % (pronoun.text, nouns))
    for noun_token in reversed(nouns):
        if noun_token:
            #print("Checking if %s is match" % noun_token.text)
            noun_is_plur = (noun_token.text.lower()[-1] == 's') and (noun_token.lemma_[-1] != 's')
            noun_is_masc = is_masculine(noun_token)
            noun_is_fem = is_feminine(noun_token)
            # match number
            if (noun_is_plur and not pron_is_sing) or \
               (not noun_is_plur and not pron_is_plur):
                # match gender
                if (noun_is_masc and not pron_is_fem) or \
                   (noun_is_fem and not pron_is_masc) or \
                   (not noun_is_fem and not noun_is_masc):
                    #print("------------------->match pronoun to %s" % noun_token.text)
                    return noun_token
    return None


class PronounReplacement:
    def __init__(self, text):
        QUEUE_SIZE = 10
        self.initial_text = text
        # deques of last noun and subject Spacy tokens
        self.last_nouns = deque([None] * QUEUE_SIZE)  # most recent last
        self.updated_text = ""


    def get_matching_noun(self, pronoun_token):
        """
        Return the last subject that matches number and gender.
        If no subject found, return the last noun to match number and gender.
        If neither found, then return the pronoun_token's text.
        """
        last_noun = match_last_pronoun(self.last_nouns, pronoun_token)
        if last_noun:
            return last_noun.text
        else:
            return pronoun_token.text


    def process_noun(self, token):
        if token.text.lower() in NOUNS_AS_PRONOUNS:
            replacement = self.get_matching_noun(token)
            #return (' >>' + token.text.upper() + ' ' + replacement + '<< ')
            return replacement
        elif u'nsubj' == token.dep_:
            update_last(self.last_nouns, token)
            return (' ' + token.text)
        else:
            update_last(self.last_nouns, token)
            return (' ' + token.text)

    
    def replace_pronouns(self):
        self.updated_text = ""
        temp = self.initial_text.replace('\n', '.\n')
        sentences = temp.split('.')
        for sent in sentences:
            tokens = nlp(unicode(sent))
            new_sent = ''
            for token in tokens:
                if token.pos_ in [u'NOUN', u'PROPN'] and u'obj' not in token.dep_:
                    new_sent += ' ' + self.process_noun(token)
                elif token.pos_ == u'ADJ' and token.dep_ == u'advcl':
                    new_sent += ' ' + self.process_noun(token)
                elif token.pos_ == u'PRON':
                    replacement = self.get_matching_noun(token)
                    #new_sent += ' >>' + token.text.upper() + ' ' + replacement + '<< '
                    new_sent += ' ' + replacement
                elif (token.pos_ == u'ADJ' and token.dep_ == u'poss') or \
                     (token.pos_ == u'PRP$'):
                    replacement = self.get_matching_noun(token)
                    #new_sent += ' >>' + token.text.upper() + ' ' + replacement + "'s<< "
                    new_sent += ' ' + replacement
                else:
                    new_sent += ' ' + repr(token)
            self.updated_text += '.  ' + new_sent


def replace_pronouns(in_str):
    replace_obj = PronounReplacement(in_str)
    replace_obj.replace_pronouns()
    return replace_obj.updated_text
