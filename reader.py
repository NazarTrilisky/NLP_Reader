import pdb
import spacy
from libs.pronouns.depronounize import replace_pronouns
from libs.question import define_comparison


TEXT_FILE_NAME = 'beauty_and_the_beast.txt'


def main():
    nlp = spacy.load('en_core_web_sm')
    with open(TEXT_FILE_NAME, 'r') as fh:
        story = fh.read()
    story = replace_pronouns(story)

    question_str = "Ask something..."
    print("\n\n\n\n\n\n\n\n\n\n\n")
    while question_str:
        question_str = raw_input("Enter a question: ")
        if not question_str:
            return
        qtokens = nlp(unicode(question_str))
        compare_obj = define_comparison(qtokens)

        sentences = story.split('.')
        NUM_MATCHES = 6
        # list of float nums 0 to 1
        match_similarities = [0 for _ in range(NUM_MATCHES)]
        # list of Spacy doc objects, containing tokens
        match_docs = [None for _ in range(NUM_MATCHES)]
        min_similarity = min(match_similarities)
        for temp_sent in sentences:
            temp_tokens = nlp(unicode(temp_sent))
            temp_similarity = compare_obj.relevancy_method(qtokens, temp_tokens)
            if temp_similarity > min_similarity:
                indx = match_similarities.index(min_similarity)
                match_similarities[indx] = temp_similarity
                match_docs[indx] = temp_tokens
                min_similarity = min(match_similarities)

        print('Question: ', question_str)
        print('Best matches:\n\n')
        no_ans = True
        NUM_TO_SHOW = 6
        sorted_indeces = sorted(range(len(match_similarities)),
                                key=lambda k: match_similarities[k]) 

        # largest similarity score first
        for indx in sorted_indeces[::-1][:NUM_TO_SHOW]:
            sent = match_docs[indx]
            ans_words, highlighted_sent = compare_obj.highlight_method(sent)
            if sent:
                print(match_similarities[indx], ans_words)
                print(repr(highlighted_sent) + '\n\n')
                no_ans = False
        if no_ans:
            print("No answers found")


if __name__ == '__main__':
    main()
