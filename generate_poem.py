import pickle
import spacy
import re
import random

#nlp = spacy.load("en_core_web_trf")

random.seed(a=None, version=2)

def generate_poem(comment_model):
    #Open the "poem model" which will be used to generate the poem with
    #"res/poemtree_markov_model_radical.pkl" is a Markov model which was trained on poem data scraped from poemtree.com
    with open("res/markov_model.pkl", "rb") as f:
        incipits, poem_model, state_size = pickle.load(f)
    
    #Accepted punctuation. The poem will generate gibberish sometimes if there are too many strange combinations of punctuation marks in sequence.
    accepted_punctuation = [",", "."]
    
    vowels = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"]
    
    #The list which will be used to store each word in the generated poem
    poem = []
    
    sequence = tuple()
    
    while((sequence not in poem_model) or (sequence[-1][0] == "punct" and sequence[-1][1] not in accepted_punctuation)):
        sequence = random.choice(incipits)
        
    #Begin the poem with a random choice of words picked from a list of incipits
    poem.extend(sequence)
    
    #A tries variable which will keep track of how many iterations the loop has been through in case the generator hits a dead-end
    tries = 0
    
    #A while loop which will continue until the poem reaches the desired length
    while(len(poem) < 100):
        #The last few words in the generated poem so far
        sequence = tuple(poem[-state_size:])
        
        #Check if the sequence is in the poem model, and check if the punctuation is acceptable.
        if((sequence not in poem_model) or (poem[-1][0] == "punct" and poem[-1][1] not in accepted_punctuation)):
            #If not then, get rid of the most recent word
            poem.pop(-1)
            
            #Return to the previous sequence, so we can generate a new word to replace the one we got rid of
            sequence = prev_seq
            
            #Increment tries variable
            tries += 1
        else:
            #If it is in the model, then keep it
            tries = 0
            
        if(poem[-1][0] == "punct"):
            print(poem[-1])
            if(poem[-1][1] not in accepted_punctuation):
                print("NOT ACCEPTABLE !")
        
        #Add a new word onto the end of the poem based on the most recent few words in the poem
        poem.append(random.choice(poem_model[sequence]))
        
        #If there have been more than 100 iterations without finding a suitable sequence of words, then the Markov model probably hit a dead-end
        if(tries > 100):
            print("Iteration failure, resetting...")
            
            #Clear the poem list
            poem = []
            
            #Start the poem again with a random choice of words
            poem.extend(random.choice(incipits))
        
        #Store the current sequence variable so we can return to it if need be
        prev_seq = sequence
    
    #Print the output which is a list of the words in the poem in sequence
    print(poem)
    
    #A string variable to store the altered poem in
    final_poem = ""
    
    prev_word = ""
    
    #Iterate through each word in the generated poem
    for token in poem:
        dep = token[0]
        tag = token[1]
        
        #Check if the dependency type is in the comment data
        if(dep in comment_model["dependencies"]):
            #Check if the tag type is in the list of dependencies
            if(tag in comment_model["dependencies"][dep]):
                #If it is, then note down one of the entries
                word_index = random.choice(comment_model["dependencies"][dep][tag])
                
                next_word = comment_model["classes"][tag][word_index]
            #If the POS type is not in the dependency data, then just place a word according to the POS attribute
            elif(tag in comment_model["classes"]):
                next_word = random.choice(comment_model["classes"][tag])
            else:
                next_word = " "
        elif(tag in comment_model["classes"]):
            next_word = random.choice(comment_model["classes"][tag])
        else:
            next_word = " "
        
        next_word = re.sub("[’]", "'", next_word)
        
        if(tag == "."):
            if(next_word == "?"):
                final_poem = final_poem[:-1] + "?"
            elif(next_word == "!"):
                final_poem = final_poem[:-1] + "!"
            else:
                next_word = "."
            
                final_poem = final_poem[:-1] + next_word
        elif(tag == ","):
            final_poem = final_poem[:-1] + ","
        elif(dep == "case"):
            final_poem = final_poem[:-1] + next_word
        elif(next_word == "i"):
            final_poem = final_poem + "I"
        elif(next_word == "n't"):
            #TODO REPLACE apostropher on all processed comments
            final_poem = final_poem + "not"
        elif(next_word == "'ll"):
            final_poem = final_poem + "will"
        elif(next_word == "'s"):
            final_poem = final_poem + "is"
        elif(next_word == "'re"):
            final_poem = final_poem + "are"
        elif(next_word == "'d"):
            final_poem = final_poem + "would"
        elif(next_word == "'ve"):
            final_poem = final_poem + "have"
        elif(prev_word == "." or prev_word == "" or prev_word == "?"):
            final_poem = final_poem + next_word.capitalize()
        elif(prev_word == "a"):
            if(next_word[0] in vowels):
                final_poem = final_poem[:-1] + "n " + next_word
        elif(prev_word == "an"):
            if(next_word[0] not in vowels):
                final_poem = final_poem[:-2] + " " + next_word
        elif(prev_word == " "):
            final_poem = final_poem[:-3] + next_word
        else:
            final_poem = final_poem + next_word
        
        final_poem = final_poem + " "
        
        prev_word = next_word
        
        #prev_seq referenced before assignment!?"
    
    print(final_poem)
    
    return final_poem
