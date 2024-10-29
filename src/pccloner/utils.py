import py7zr, zipfile, os

def zip_folder_in_chunks(folder_path, output_zipfile_base, chunk_size):
    current_chunk = 1
    current_size = 0
    output_zipfile = f"{output_zipfile_base}_part{current_chunk}.zip"
    
    # Create a new zip file
    zipf = zipfile.ZipFile(output_zipfile, 'w', zipfile.ZIP_DEFLATED)

    # Walk through the folder structure
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Calculate the file size
            file_size = os.path.getsize(file_path)
            
            # If adding the file exceeds the chunk size, create a new zip file
            if current_size + file_size > chunk_size:
                zipf.close()  # Close the current zip file
                current_chunk += 1
                output_zipfile = f"{output_zipfile_base}_part{current_chunk}.zip"
                zipf = zipfile.ZipFile(output_zipfile, 'w', zipfile.ZIP_DEFLATED)
                current_size = 0  # Reset the current size

            # Add the file to the zip
            arcname = os.path.relpath(file_path, folder_path)  # Preserve the folder structure
            zipf.write(file_path, arcname)
            current_size += file_size  # Update the current size of the zip

    zipf.close()  # Close the final zip file

def extract_zip_chunks(output_zipfile_base, output_folder):
    current_chunk = 1
    while True:
        zip_file_name = f"{output_zipfile_base}_part{current_chunk}.zip"
        if not os.path.exists(zip_file_name):
            break  # No more zip files to extract

        # Extract the current chunk
        with zipfile.ZipFile(zip_file_name, 'r') as zipf:
            zipf.extractall(output_folder)
        current_chunk += 1

### Slower, but less memory space e.g. 6.3min to compress 3.8GB into 388MB
def compress_to_7z(input_path, output_archive, chunk_size=2*1024*1024*1024): 
    """
    Compresses a file or directory into a .7z archive and splits it into chunks.
    """
    with py7zr.SevenZipFile(output_archive, 'w') as archive:
        archive.writeall(input_path, os.path.basename(input_path))
    file_size = os.path.getsize(output_archive)
    if file_size > chunk_size:
        print(f"File size: {file_size}. Splitting the archive into {chunk_size} byte chunks.")
        with open(output_archive, 'rb') as f:
            chunk_num = 1
            while chunk := f.read(chunk_size):
                chunk_filename = f"{output_archive}.{chunk_num:03d}"
                with open(chunk_filename, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                chunk_num += 1
        os.remove(output_archive)
        print(f"Split into {chunk_num - 1} chunks.")
    else:
        print(f"No need to split. Archive size is within the limit.")


def join_7z_chunks(output_archive, chunk_folder):
    """
    Joins chunked .7z files back into a single archive.
    :param output_archive: The name of the output combined .7z archive.
    :param chunk_folder: The folder where the chunk files are stored.
    """
    chunk_number = 1
    with open(output_archive, 'wb') as output_file:
        while True:
            chunk_filename = os.path.join(chunk_folder, f"{output_archive}.{chunk_number:03d}")
            if not os.path.exists(chunk_filename):
                print(f"Chunk {chunk_filename} does not exist. Stopping.")
                break
            
            print(f"Joining chunk {chunk_filename}...")
            with open(chunk_filename, 'rb') as chunk_file:
                output_file.write(chunk_file.read())
            
            chunk_number += 1
    print(f"All chunks joined into {output_archive}.")
