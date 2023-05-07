def load_label_table():
    with open("label.txt", "r") as f:
        loaded = f.readlines() 
    processed = [l.replace("\n", "").split(" ") for l in loaded]
    return processed

def stoi(label_table, label):
    label = label.replace(" ", "_")
    for i, labels in enumerate(label_table):
        if label in labels:
            return i
    return -1

def itos(label_table, index):
    return label_table[index]