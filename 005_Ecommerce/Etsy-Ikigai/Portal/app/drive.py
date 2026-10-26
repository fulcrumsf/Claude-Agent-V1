"""Google Drive helper for the package step. Auth: ~/.config/agent-os-drive/token.json
(made by 001_Architecture/Scripts/google_drive_auth.py, account info@borednomad.com)."""
import os
import re

TOKEN_PATH = os.path.expanduser("~/.config/agent-os-drive/token.json")
IKIGAI_FOLDER_ID = "16zSQOE4UeRYvMyZrE5llaNgR-ZWZ4YsQ"  # "Ikigai Digital Studio"


def next_sequence(names):
    """Next folder number from names like '00084-Edo Ginkgo Leaf'; gaps are not reused."""
    nums = [int(m.group(1)) for n in names if (m := re.match(r"^(\d{5})-", n))]
    return max(nums, default=0) + 1


def folder_name(seq, title):
    return f"{seq:05d}-{title.strip()}"


def service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from .pipeline.base import NotConfigured
    if not os.path.exists(TOKEN_PATH):
        raise NotConfigured("Drive: run google_drive_auth.py to log in as info@borednomad.com")
    return build("drive", "v3", credentials=Credentials.from_authorized_user_file(TOKEN_PATH))


def create_listing_folder(title, parent=IKIGAI_FOLDER_ID):
    d = service()
    res = d.files().list(q=f"'{parent}' in parents and trashed=false", fields="files(name)", pageSize=1000).execute()
    name = folder_name(next_sequence([f["name"] for f in res["files"]]), title)
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent]}
    return d.files().create(body=meta, fields="id,name,webViewLink").execute()


def upload_file(path, parent_id):
    from googleapiclient.http import MediaFileUpload
    meta = {"name": os.path.basename(path), "parents": [parent_id]}
    return service().files().create(body=meta, media_body=MediaFileUpload(path, resumable=True),
                                    fields="id,name,webViewLink").execute()
