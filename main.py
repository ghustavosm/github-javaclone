import os
import csv
import glob
import requests
import subprocess


def get_token():
    with open("token.txt", "r") as open_file:
        content = open_file.readlines()

    token = ""
    for line in content:
        if line.startswith("token"):
            token = line.strip().split("=")[1]

    if not token:
        raise Exception("Token not configured error")

    return token


def download_file(destination_path, student):
    url = f"{student['student_repository_url']}/zipball/master/"
    headers = {
        "Authorization": f"token {get_token()}",
        "Accept": 'application/vnd.github.v3+json',
    }
    request = requests.get(url, headers=headers)

    if request.status_code == 200:
        file_name = f"{student['assignment_name']}_{student['github_username']}.zip"
        print(f"Downloading... {file_name} [{len(request.content)} bytes]")
        with open(f"{destination_path}/{file_name}", "wb") as open_file:
            open_file.write(request.content)
    else:
        raise Exception("Error accessing repository.")


def download_files(csv_file, destination_path):
    with open(csv_file, encoding='utf8') as f:
        data = csv.DictReader(f)
        for student in data:
            download_file(destination_path, student)


def run_process(csv_file, destination_path):
    try:
        download_files(csv_file, destination_path)
    except Exception as e:
        raise Exception(e)
    else:
        print("Running javaclone...")
        process = subprocess.run(["python", "../javaclone/javaclone/main.py", destination_path])
        if process.returncode != 0:
            raise Exception("Error running javaclone.")


def clean_folder(folder):
    files = glob.glob(f"{folder}/*")
    for f in files:
        try:
            os.remove(f)
        except Exception:
            raise Exception(f"Error removing {f} file")


def create_folder(folder):
    if not os.path.isdir(folder):
        print("Creating download folder...")
        try:
            os.mkdir(folder)
        except Exception:
            raise Exception("Error creating folder")
    else:
        print("The folder already exists.")
        print("Removing files from the folder...")
        clean_folder(folder)


def get_csv_file():
    files = glob.glob("*.csv")
    for f in files:
        return f

    raise Exception("CSV file not found.")


def main():
    try:
        csv_file = get_csv_file()
        destination_path = "repositories"
        create_folder(destination_path)
        run_process(csv_file, destination_path)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
