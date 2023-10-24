import sys
from datetime import datetime
import sys

"""
    This file manages the script that makes sure that all the console output is also written to a log file
    in the logs/ directory
"""

# Define a custom stream to capture the output from the commandline
class CustomStream:
    def __init__(self, original):
        self.log_buffer = []
        self.original = original
    
    def write(self, text):
        self.original.write(text)
        self.log_buffer.append(text)
    
    def flush(self):
        pass

''' 
    Initialize the custom stream
'''
def init_custom_stream():
    # Store the original standard output
    original_stdout = sys.stdout
    # Create a timestamp for when the code is executed
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Create an instance of the custom stream
    custom_stream = CustomStream(original_stdout)
    # Redirect the standard output to the custom stream
    sys.stdout = custom_stream

    return original_stdout,timestamp,custom_stream

''' 
    Write the current stdout to a log file
    @param: original_stdout, the original stdout output
    @param: timestamp, use timestamp in the name to make it unique
    @param: custom_stream, custom_stream object containing the log buffer
    @param: log_file_name, the log filename
'''
def write_log(original_stdout, timestamp, custom_stream, log_file_name):
    # Restore the original standard output
    sys.stdout = original_stdout

    # Define a file name for the log
    log_file = f"logs/log-{timestamp}.txt"

    # Write the captured output to a file with a timestamp
    with open(log_file, "a") as f:
        f.write(f"{log_file_name}\n")
        f.write(f"Execution Timestamp: {timestamp}\n")
        for text in custom_stream.log_buffer:
            f.write(text)

    print(f"Output has been saved to {log_file}")
