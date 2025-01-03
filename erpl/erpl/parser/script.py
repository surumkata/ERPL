file = open("grammar_erpl.txt")

lines = file.read().split("\n")

file2 = open("test.py","w+")

for line in lines:
    line.strip()
    termos = line.split(":")
    termo = termos[0].strip()
    if(len(termos) > 1):
        file2.write(f"def {termo}(self,{termo}):\n")
        file2.write(f"    '''{line}'''\n")
        file2.write(f"    children = {termo}.children\n")
        file2.write("\n")