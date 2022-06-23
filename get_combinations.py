possible_strings = []
iterate_string = "gyz"

def backtracking(cur_str):
    if len(cur_str) == 5:
        possible_strings.append(cur_str)
        return
    
    for i in range(len(iterate_string)):
        
        cur_str += iterate_string[i]
        backtracking(cur_str)
        cur_str = cur_str[:-1]

    return possible_strings

backtracking("")
#print(possible_strings)
#print(len(possible_strings))
    