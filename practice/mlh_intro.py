import time 
import random 

# sample sentences 
sentences = [ 
    "The quick brown fox jumps over the lazy dog.", 
    "Python is a great programming language.", 
    "I love watching dominosaurs streams!", 
    "Coding is fun and rewarding.", 
    "Practice makes perfect." 
]

# initial prompt 
print("Welcome to the Typing Speed Test!")
print("you will get a sentence to type!")
print("Press enter when you're ready\n")
input("press enter to begin")

sentence = random.choice(sentences)
print("\ntype this sentence:")
print(sentence)
print()

input("press enter when you're ready")

# start timer
start_time = time.time()
typed_input = input("\nstart typing\n")
end_time = time.time()

#calculate time overall 
overall = end_time - start_time
overall = round(overall, 2)

# calculate wpm
count = len(typed_input.split())
wpm = round(count / (overall / 60))

# typing errors
errors = 0 
for i in range(min((len(sentence)), len(typed_input))):
    if sentence[i] != typed_input[i]:
        errors += 1

# add penalty 
errors += abs(len(sentence) - len(typed_input))

# results
print("\ntotal time: " + str(overall) + " seconds")
print("typing speed:" + str(wpm) + " wpm")
print("total errors: " + str(errors))

print("\nthanks for playing our typing test!")