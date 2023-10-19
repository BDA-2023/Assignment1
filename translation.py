def open_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None

def read_line_as_string(file):
    if file:
        line = file.readline()
        if line:
            return line.strip()  # Remove any leading/trailing whitespace
        else:
            print("End of file reached.")
    else:
        print("File is not open.")
    return None

# Example usage:
file_path = 'small-xmlparsed.txt'  # Replace with the path to your text file
file = open_text_file(file_path)

if file:
    line = read_line_as_string(file)
    while line:
        print(line)
        line = read_line_as_string(file)

file.close()  # Close the file when you're done with it
