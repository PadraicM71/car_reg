import os
import requests

# File API interaction functions
# This file interacts with a custom File API, providing functionality for health checks, file uploads, 
# downloads, listing, and deletions.

# I CREATED THIS FILE TO INTERACT WITH THE API I BUILT - THIS FILE CAN BE CHANGED FOR EACH INDIVIDUAL 
# PROJECT - KEEP ORIGIONAL SERVER API UNCHANGED
# I PLAN TO PUT THIS FILE IN THE DIRECTORY OF EACH NEW PROJECT!

# A BACKUP COPY OF PYTHON FILE ON UBUNTU SERVER OS STORED IN DIRECTORY app_on_server
# DO NOT COPY AND PASTE THESE COMMENTS:
# need to enter below in terminal for testing:  (DO NOT EXPOSE THIS KEY ANYWHERE ELSE!!!)
# export FILE_API_KEY="AefjFQqY6lPLZaFaP63jS8D8QfWcfPxks3-5t8T-DlQ"

# SEE INSTRUCTIONS ON GOOGLE DOC FOR USING THIS API


FILE_API_URL = os.environ.get(
    "FILE_API_URL",
    "https://files.moranai.net"
)

FILE_API_KEY = os.environ.get("FILE_API_KEY")


def _get_headers():
    """
    Return the authentication headers required by the File API.
    """

    if not FILE_API_KEY:
        raise ValueError(
            "FILE_API_KEY environment variable is not configured"
        )

    return {
        "X-API-Key": FILE_API_KEY
    }


def health_check():
    """
    Check whether the File API is running.

    Returns:
        dict: API response
    """

    response = requests.get(
        f"{FILE_API_URL}/health",
        timeout=30
    )

    response.raise_for_status()

    return response.json()



def upload_file(file_path, app, folder="", filename=None):
    """
    Upload a file to the File API.

    Args:
        file_path (str): Local path of the file to upload
        app (str): Application name
        folder (str, optional): Folder within the application
        filename (str, optional): Filename to use when stored on the server

    Returns:
        dict: API response
    """

    with open(file_path, "rb") as file:

        # If no filename supplied, use the local filename
        if filename is None:
            filename = os.path.basename(file_path)

        files = {
            "file": (filename, file)
        }

        data = {
            "app": app,
            "folder": folder
        }

        response = requests.post(
            f"{FILE_API_URL}/upload",
            headers=_get_headers(),
            files=files,
            data=data,
            timeout=120
        )

    response.raise_for_status()

    return response.json()



def download_file(app, filename, output_path, folder=""):
    """
    Download a file from the File API.

    Args:
        app (str): Application name
        filename (str): Name of the file on the server
        output_path (str): Local path where the file will be saved
        folder (str, optional): Folder within the application

    Returns:
        str: Path of the downloaded file
    """

    params = {
        "app": app,
        "folder": folder,
        "file": filename
    }

    response = requests.get(
        f"{FILE_API_URL}/download",
        headers=_get_headers(),
        params=params,
        timeout=120
    )

    response.raise_for_status()

    with open(output_path, "wb") as file:
        file.write(response.content)

    return output_path


def list_files(app, folder=""):
    """
    Get a list of files from the File API.

    Args:
        app (str): Application name
        folder (str, optional): Folder within the application

    Returns:
        dict: API response
    """

    params = {
        "app": app,
        "folder": folder
    }

    response = requests.get(
        f"{FILE_API_URL}/list",
        headers=_get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def delete_file(app, filename, folder=""):
    """
    Delete a file from the File API.

    Args:
        app (str): Application name
        filename (str): Name of the file to delete
        folder (str, optional): Folder within the application

    Returns:
        dict: API response
    """

    params = {
        "app": app,
        "folder": folder,
        "file": filename
    }

    response = requests.delete(
        f"{FILE_API_URL}/delete",
        headers=_get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

