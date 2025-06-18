file = open("info.settings", "r")
info = []
text = file.read().split("\n")
for i in range(len(text)):
    info.append(text[i].split(" :: "))
    del info[i][0]

output = str(info[0][0][2:-1])
user_input = str(info[1][0][2:-1])
gui = str(info[2][0][2:-1])

file.close()


def return_info():
    return output, user_input, gui
