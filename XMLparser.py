import xml.etree.ElementTree as ET

# Define a sample XML string for parsing (you can also read from a file)
xml_data = """
<root>
    <person>
        <name>John</name>
        <age>30</age>
    </person>
    <person>
        <name>Alice</name>
        <age>25</age>
    </person>
</root>
"""

# Parse the XML data
root = ET.fromstring(xml_data)

# Traverse and access elements and attributes
for person in root.findall('person'):
    name = person.find('name').text
    age = person.find('age').text
    print(f"Name: {name}, Age: {age}")
