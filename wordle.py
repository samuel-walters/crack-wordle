import random
import csv
import copy
from get_combinations import possible_strings
from wordfreq import word_frequency

# A CSV file containing the words that wordle accepts (excluding the words in the answer list)

with open("accepted_words.csv", newline='') as f:
    reader = csv.reader(f)
    accepted = list(reader)

# A CSV file containing all the words that are an answer on a specific day

with open("answers.csv", newline='') as f:
    reader = csv.reader(f)
    answers = list(reader)

# data contains every possible word you can guess on wordle    
data = accepted + answers

class Wordle():
    def __init__(self):
        # Our current list of possible guesses
        self.word_lst = [x for sub in data for x in sub]
        # Every single word in the list of Wordle's accepted five letter words
        self.unchanging_lst = self.word_lst.copy()
        # The answer word (chosen at random from answers.csv)
        self.word = random.choice(answers[0])
        # A dictionary which holds the frequency of each letter
        # in the answer. This will be of use when words have more
        # than one letter and we have to narrow down our guesses.
        self.multiple_letters = {}
        for letter in self.word:
            if letter in self.multiple_letters:
                self.multiple_letters[letter] += 1
            else:
                self.multiple_letters[letter] = 1
        # A dictionary that will record the currently known frequency
        # of each letter appearing in the answer. This will be updated 
        # each time we make a guess.
        self.known_letter_frequency = {}
        # A list that contains all the green letters we have got so far.
        self.perfect = ["","","","",""]
        # A dictionary that contains all the yellow letters.
        self.inside = {}
        # A dictionary containing all the grey letters.
        self.outside = {}
        # This dictionary will record how many letters appear in the remaining
        # guess list. For example, it will contain key:value pairs  
        # like 'a':192', 'e':127 etc.
        self.remaining_letters = {}
        self.win = False
        self.guesses = 0
        self.gain_more_info = True

    def guess(self, guess):
        self.guesses += 1
        letters_used = {}
        for idx, letter in enumerate(guess):
            # If the letter is in the word...
            if letter in self.multiple_letters:
                if letter in letters_used:
                    letters_used[letter] += 1
                else:
                    letters_used[letter] = 1
                # If our guess contains a letter more times than it appears in 
                # the actual answer word, than we shall simply pass without updating
                # our known_letter_frequency dictionary.     
                if letters_used[letter] > self.multiple_letters[letter]:
                    pass
                else:
                    # Updating the known_letter_frequency dictionary as the frequency of the letter in our guess
                    # so far is at least less than or equal to the number of times it actually appears in the answer
                    if letter in self.known_letter_frequency:
                        self.known_letter_frequency[letter] = max(self.known_letter_frequency[letter], letters_used[letter])
                    else:
                        self.known_letter_frequency[letter] = 1

            # Deals with green letters
            if guess[idx] == self.word[idx]:
                self.perfect[idx] = letter
            # Deals with yellow letters
            elif letter in self.word:
                if letter not in self.inside:
                    self.inside[letter] = [idx]
                else:
                    if idx not in self.inside[letter]:
                        self.inside[letter] = self.inside[letter] + [idx]
            # Deals with grey letters
            else:
                self.outside[letter] = True
        
        if "" not in self.perfect:
            self.win = True

    def narrow_words(self):
        # As we iterate through our possible answers list, we shall be
        # removing words if they don't match certain criteria. As such,
        # this pop_counter variable will help us avoid index errors
        # as we iterate through a list we are updating. 
        pop_counter = 0
        for i in range(len(self.word_lst)):
            # Bool variable that keeps track of whether we should
            # continue with the current iteration
            still_good = True
            # Dictionary that records the frequency of each letter
            guess_frequency = {}
            for letter in self.word_lst[i - pop_counter]:
                if letter in guess_frequency:
                    guess_frequency[letter] += 1
                else:
                    guess_frequency[letter] = 1

            # Checks if the currently known frequency of letters in the answer
            # matches the current guess's frequency of letters.
            for key, value in self.known_letter_frequency.items():
                # Letters we know are in the answer aren't in the current word at all,
                # so we shall pop it from the words list.
                if key not in guess_frequency:
                    self.word_lst.pop(i - pop_counter)
                    pop_counter += 1
                    still_good = False
                    break
                else:
                    # If this guess word uses a letter fewer times than we know it
                    # appears in the answer, then we shall also pop it
                    if guess_frequency[key] < value:
                        self.word_lst.pop(i - pop_counter)
                        pop_counter += 1
                        still_good = False
                        break
                    # If the sum of the values in the known_letter_frequency dictionary is 5
                    # (meaning we know how many times every letter appears), and if the current
                    # guess uses a letter more times than it appears in the known_letter_frequency
                    # dictionary, it must also be popped
                    if sum(self.known_letter_frequency.values()) == 5:
                        if guess_frequency[key] > value:
                            self.word_lst.pop(i - pop_counter)
                            pop_counter += 1
                            still_good = False
                            break
            if still_good == False:
                continue
            # Checks if it contains letters we know are not in the word
            for letter in self.word_lst[i - pop_counter]:
                if letter in self.outside and letter not in self.inside and letter not in self.perfect:
                    self.word_lst.pop(i - pop_counter)
                    pop_counter += 1
                    still_good = False
                    break
            if still_good == False:
                continue
            # Checks whether letters in the word are in places we know
            # they should not be in. 
            for letter in self.inside.keys():
                if still_good == False:
                    break
                for place in self.inside[letter]:
                    if letter == self.word_lst[i - pop_counter][place]:
                        self.word_lst.pop(i - pop_counter)
                        pop_counter += 1
                        still_good = False
                        break
            if still_good == False:
                continue
            # Checks if the word contains letters
            # in the right positions
            for idx, letter in enumerate(self.perfect):
                if letter != "":
                    if self.word_lst[i - pop_counter][idx] != self.perfect[idx]:
                        self.word_lst.pop(i - pop_counter)
                        pop_counter += 1
                        still_good = False
                        break

        return self.word_lst

    def letters_in_last_words(self):
        # a dictionary that tracks the number of each remaining letter (for example 'a': 24, 'b': 0, 'c': 2 etc.)
        self.remaining_letters = {}
        for word in self.word_lst:
            for letter in word:
                if letter in self.remaining_letters:
                    self.remaining_letters[letter] += 1
                else:
                    self.remaining_letters[letter] = 1

    def machine_placement_guess(self):
        letter_position_count = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}

        for word in self.word_lst:
            for idx, letter in enumerate(word):
                if letter in letter_position_count[idx]:
                    letter_position_count[idx][letter] += 1
                else:
                    letter_position_count[idx][letter] = 1

        best_count = 0
        best_word = ""

        for word in self.unchanging_lst:
            count = 0
            seen = {}
            consider = True
            for idx, letter in enumerate(word):
                if letter in self.inside or letter in self.outside or letter in self.perfect:
                    consider = False
                    break
                if self.gain_more_info == True:
                    if letter not in self.remaining_letters:
                        consider = False
                        break
                    if letter in seen:
                        consider = False
                        break
                if letter in letter_position_count[idx]:
                    count += letter_position_count[idx][letter]
                if letter not in seen:
                    if letter in self.remaining_letters:
                        count += self.remaining_letters[letter]
                        seen[letter] = True
            if consider == True:
                if count > best_count:
                    best_count = count
                    best_word = word

        if best_word != "":
            return best_word
        else:
            if self.gain_more_info == True:
                self.gain_more_info = False
                return self.machine_placement_guess()
            return False

    def machine_next_guess(self):
        letter_position_count = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}
        for word in self.word_lst:
            for idx, letter in enumerate(word):
                if letter in letter_position_count[idx]:
                    letter_position_count[idx][letter] += 1
                else:
                    letter_position_count[idx][letter] = 1

        word_count = {}
        for word in self.word_lst:
            count = 0
            seen = {}
            for letter in word:
                if letter in letter_position_count[idx]:
                    count += letter_position_count[idx][letter]
                if letter in seen:
                    continue
                seen[letter] = True
                if letter in self.remaining_letters:
                    count += self.remaining_letters[letter]
            word_count[word] = count 
        new_lst = sorted(word_count.values())
        return list(word_count.keys())[list(word_count.values()).index(new_lst[len(new_lst) // 2])]

    def look_ahead_guess(self):
        highest_score = 0
        average_score = 0
        best_word = ""
        for word in self.word_lst:
            score = 0
            for string in possible_strings:
                copied_obj = copy.deepcopy(self)
                skip_iteration = False
                for i in range(len(string)):
                    if string[i] == "g":
                        if copied_obj.perfect[i] != "":
                            if copied_obj.perfect[i] == word[i]:
                                pass
                            else:
                                skip_iteration = True
                                break
                        else:
                            copied_obj.perfect[i] = word[i]
                    elif string[i] == "y":
                        if word[i] not in copied_obj.inside:
                            if word[i] in copied_obj.outside or word[i] == copied_obj.perfect[i]:
                                skip_iteration = True
                                break
                            copied_obj.inside[word[i]] = [i]
                        else:
                            if i not in copied_obj.inside[word[i]]:
                                if word[i] in copied_obj.outside or word[i] == copied_obj.perfect[i]:
                                    skip_iteration = True
                                    break
                                copied_obj.inside[word[i]] = copied_obj.inside[word[i]] + [i]
                    elif string[i] == "z":
                        if word[i] in copied_obj.inside or word[i] in copied_obj.perfect:
                            skip_iteration = True
                            break
                        copied_obj.outside[word[i]] = True
                if skip_iteration == False:
                    copied_obj.narrow_words()
                    new_length = len(copied_obj.word_lst)
                    if new_length != 0:
                        possibility = new_length / len(self.word_lst)
                        difference = len(self.word_lst) - new_length
                        score += (possibility * difference)
    
            average_score = score / len(possible_strings)
            if average_score >= highest_score:
                highest_score = average_score
                best_word = word

        return best_word
    
    def eliminate_similar_words(self):
        dic = {0: {}, 1: {}, 2: {}, 3:{}, 4:{}}
        for string in self.word_lst:
            for j, letter in enumerate(string):
                if letter in dic[j]:
                    dic[j][letter] += 1
                else:
                    dic[j][letter] = 1

        count_same_letters = 0
        for key in dic.keys():
            if max(dic[key].values()) > len(self.word_lst) // 2:
                count_same_letters += 1
            else:
                special_key = key

        if count_same_letters == 4:
            best_count = 0
            best_word = ""
            for word in self.unchanging_lst:
                count_same_letters = 0
                already_seen = {}
                for letter in word:
                    if letter in already_seen:
                        continue
                    if letter in dic[special_key]:
                        already_seen[letter] = True
                        count_same_letters += 1

                if count_same_letters > best_count:
                    best_count = count_same_letters
                    best_word = word
            return best_word
        return False

    def word_frequency_guess(self):
        best_count = 0
        best_word = ""
        for word in self.word_lst:
            score = word_frequency(word, "en")
            if score > best_count:
                best_count = score
                best_word = word
        return best_word

if __name__ == "__main__":
    obj = Wordle()
    while obj.guesses < 6 and obj.win == False:
        guess = input("Guess a five letter word: ").lower()
        while len(guess) != 5:
            guess = input("Ensure it is five letters long: ").lower()
        obj.guess(guess)
        if obj.guesses == 6:
            break
        print("Perfect: " + str(obj.perfect))
        print("Contains: " + str(obj.inside))
        print("Excludes: " + str(obj.outside))
        print("Guess: " + str(obj.guesses))
        print("\n")

        print(obj.narrow_words())
        obj.letters_in_last_words()
        print("The first machine guess: " + str(obj.machine_placement_guess()))
        print("Out of the remaining words the machine then guessed: " + str(obj.machine_next_guess()))
        print("Word frequency guess: " + str(obj.word_frequency_guess()))
        if obj.guesses < 5:
            if len(obj.word_lst) < 20:
                a = obj.eliminate_similar_words()
                if a != False:
                    print("To eliminate similar words, the algorithm wants you to use the word '" + str(a) + "'.")
        #if len(obj.word_lst) <= 14 and len(obj.word_lst) > 2:
        #    print("Please wait...")
        #    print("Other guess that looks ahead to narrow down possibilities: " + str(obj.look_ahead_guess()))

    if obj.win == True:
        print("You won! The word was indeed " + str(obj.word) + "!")
    elif obj.win == False:
        print("You lost. The word was " + str(obj.word) + ".")



    
