from wordle import Wordle
obj = Wordle()
obj.multiple_letters = {}

print("Input the green letters as g, the yellow letters as y, and the grey letters as z")
print("For example, if your guess yields all grey letters you would enter zzzzz")
print("\n")
while obj.guesses < 6 and obj.win == False:
    # At the start, the algorithm always chooses "tares". To save time,
    # this guess will immediately be inputted.
    if obj.guesses == 0:
        algorithm_guess = "tares"
    elif obj.guesses == 5 or len(obj.word_lst) <= 2:
            algorithm_guess = obj.word_frequency_guess()
    else:
        obj.letters_in_last_words()
        if len(obj.word_lst) <= 13:
            a = obj.eliminate_similar_words()
            if a != False and obj.guesses < 5:
                algorithm_guess = a
            else:
                algorithm_guess = obj.machine_next_guess()
        else:
            algorithm_guess = obj.machine_placement_guess()
            if algorithm_guess == False:
                algorithm_guess = obj.machine_next_guess()
    
    print("The machine's guess: " + str(algorithm_guess) + ".")
    your_guess = input("enter the word you wish to guess: ").lower()
    string_input = input("Enter the result of your guess: ")
    if string_input == "ggggg":
        print("You won! Stop typing in console.")
        break
    print("\n")

    # Gets the known frequency of letters in the answer we just learnt
    # from our current guess
    current_frequency = {}

    for i in range(len(your_guess)):
        if string_input[i] == "g":
            obj.perfect[i] = your_guess[i]
            if your_guess[i] not in current_frequency:
                current_frequency[your_guess[i]] = 1
            else:
                current_frequency[your_guess[i]] += 1
        elif string_input[i] == "y":
            if your_guess[i] not in obj.inside:
                obj.inside[your_guess[i]] = [i]
            else:
                if i not in obj.inside[your_guess[i]]:
                    obj.inside[your_guess[i]] = obj.inside[your_guess[i]] + [i]
            if your_guess[i] not in current_frequency:
                current_frequency[your_guess[i]] = 1
            else:
                current_frequency[your_guess[i]] += 1
        elif string_input[i] == "z":
            obj.outside[your_guess[i]] = True

    # updates our dictionary that keeps track of how many times we (at present) know each
    # letter appears in the answer
    for key, value in current_frequency.items():
        if key not in obj.known_letter_frequency:
            obj.known_letter_frequency[key] = value
        else:
            obj.known_letter_frequency[key] = max(obj.known_letter_frequency[key], value)
    obj.guesses += 1
    obj.narrow_words()