file = open("info.settings", "r")
info = []
text = file.read().split("\n")
for i in range(len(text)):
    info.append(text[i].split(" = "))
    del info[i][0]

output = str(info[0][0])
user_input = str(info[1][0])
gui = str(info[2][0])

file.close()

if output == "audio":
    output = True
elif output == "text":
    output = False

if user_input == "audio":
    user_input = True
elif user_input == "text":
    user_input = False

if gui == "true":
    gui = True
elif gui == "false":
    gui = False


def return_info():
    return output, user_input, gui
