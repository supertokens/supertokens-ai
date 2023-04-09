def get_multi_line_input():
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    
    inp = "\n".join(contents)
    if inp == "exit":
        quit()
    return inp