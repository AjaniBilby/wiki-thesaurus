import requests
import bz2
import os

# Set the URL of the file to download
url = 'https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-articles.xml.bz2'

# Set the path of the directory where the file will be saved
dir_path = 'data'

# Create the directory if it doesn't exist
if not os.path.exists(dir_path):
  os.makedirs(dir_path)

# Set the path of the file to be saved
file_path = os.path.join(dir_path, 'simplewiki-latest-pages-articles.xml')

# Download the file
response = requests.get(url, stream=True)

# Save the file to disk
with open(file_path + '.bz2', 'wb') as f:
    bytes_so_far = 0
    for data in response.iter_content(chunk_size=1024):
        bytes_so_far += len(data)
        f.write(data)
        print(f'Downloaded {(bytes_so_far/1048576):.2f}MB', end='\r')

# Extract the file
with open(file_path + '.bz2', 'rb') as f:
    decompressor = bz2.BZ2Decompressor()
    with open(file_path, 'wb') as outfile:
        bytes_so_far = 0
        for data in iter(lambda : f.read(100 * 1024), b''):
            bytes_so_far += len(data)
            outfile.write(decompressor.decompress(data))
            print(f'Extracted {(bytes_so_far/1048576):.2f}MB', end='\r')

# Remove the compressed file
os.remove(file_path + '.bz2')

print(f'Download and extraction of {file_path} complete!')