import os
import shutil

def split_file(file_path, output_dir):
    max_size = 50 * 1024 * 1024  # 50 MB in bytes
    file_size = os.path.getsize(file_path)

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    if file_size <= max_size:
        output_file_path = os.path.join(output_dir, os.path.basename(file_path))
        shutil.copyfile(file_path, output_file_path)
        return

    with open(file_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk_data = f.read(max_size)
            if not chunk_data:
                break
            chunk_num += 1
            chunk_filename = os.path.join(output_dir, f"{os.path.basename(file_path)}.part{chunk_num}")
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk_data)


def combine_files(input_dir, output_path):
    files = os.listdir(input_dir)
    if len(files) == 1:
        input_file_path = os.path.join(input_dir, files[0])
        shutil.copyfile(input_file_path, output_path)
        return

    with open(output_path, 'wb') as f:
        for filename in sorted(files):
            if not filename.startswith(os.path.basename(output_path)):
                continue
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'rb') as chunk_file:
                f.write(chunk_file.read())

# loop through all files in processed directory
if os.path.exists('processed'):
    for file in os.listdir('processed'):
        # get file name along with extension
        file_name = os.path.basename(file)
        split_file('processed/' + file_name, 'chunks/' + file_name)
else:
    os.makedirs("processed")
    for file in os.listdir('chunks'):
        # get file name along with extension
        file_name = os.path.basename(file)
        combine_files('chunks/' + file_name, 'processed/' + file_name)