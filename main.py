import re
import os
import shutil
import requests
from tqdm import tqdm


def create_directories():
    os.makedirs('raw', exist_ok=True)
    os.makedirs('output', exist_ok=True)


def clean_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            os.remove(os.path.join(directory, file))


def read_urls(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def download_urls(urls):
    for count, url in enumerate(urls):
        filename = f"raw/{count}.txt"
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('Content-Length', 0))

        with open(filename, 'w', encoding='utf-8', errors='replace') as file, tqdm(
                desc=f"Downloading {count}",
                total=total_size,
                unit='B',
                unit_scale=True) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    try:
                        file.write(chunk.decode('utf-8'))
                    except UnicodeDecodeError:
                        file.write(chunk.decode('utf-8', errors='replace'))
                    bar.update(len(chunk))


def download_whitelist():
    url = "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt"
    response = requests.get(url)
    return set(line.strip().lower() for line in response.text.splitlines())


def process_files():
    domain_pattern = re.compile(r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})')
    with open('output/raw.txt', 'w', encoding='utf-8') as output_file:
        for filename in os.listdir('raw'):
            if filename.endswith('.txt'):
                with open(os.path.join('raw', filename), 'r', encoding='utf-8', errors='replace') as file:
                    for line in file:
                        match = domain_pattern.search(line.strip())
                        if match:
                            output_file.write(f"{match.group(0)}\n")


def clean_and_sort_raw(whitelist):
    with open('output/raw.txt', 'r', encoding='utf-8') as f:
        lines = sorted(set(line.strip().lower() for line in f.readlines() if line.strip().lower() not in whitelist))

    # Prepend '0.0.0.0' to each line
    with open('output/unique.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(f"0.0.0.0 {line}\n")


def main():
    create_directories()
    clean_directory('raw')
    clean_directory('output')

    urls = read_urls('sources.txt')

    print("Downloading hosts...")
    download_urls(urls)

    print("\nProcessing files...")
    process_files()

    print(f"File size of raw.txt: {os.path.getsize('output/raw.txt')} bytes")

    print("\nDownloading the whitelist...")
    whitelist = download_whitelist()

    print("\nCleaning and sorting raw file...")
    clean_and_sort_raw(whitelist)

    print(f"File size of unique.txt: {os.path.getsize('output/unique.txt')} bytes")

    shutil.copy('output/unique.txt', '..')


if __name__ == "__main__":
    main()
