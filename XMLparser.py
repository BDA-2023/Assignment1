import xml.etree.ElementTree as ET

# Specify the path to your XML file
smallxml = 'small-dblp.xml'
bigxml = 'big-dblp.xml'

# Parse the XML file
tree = ET.parse(smallxml)
root = tree.getroot()

def printTitleAndYearFor(root):
    for article in root.findall('article'):
        title = article.find('title').text
        year = article.find('year').text
        print(f"Title: {title}, Year: {year}")

def printAuthorsPer(documentType, root):
    for article in root.findall(documentType):
        line = ""
        authors = article.findall('author')
        for author in authors:
            line += f"{author.text}," 
            #print(f"{author.text}", end=",")
        append_to_file(line)
        append_to_file("\n")
        #print()

def append_to_file(string_to_append):
    file_name = "xmlparsed.txt"
    with open(file_name, 'a') as file:
        file.write(string_to_append)


print("=========== articles ===========")
printAuthorsPer('article', root)
print("=========== proceedings ===========")
printAuthorsPer('proceedings', root)
print("=========== in proceedings ===========")
printAuthorsPer('inproceedings', root)