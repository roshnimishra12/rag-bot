# gdocs.py
from googleapiclient.discovery import build
from auth import credentials_from_json
from typing import List

def list_google_docs(creds_json: dict) -> List[dict]:
    """
    Returns list of Google Docs files (id, name) from Drive.
    """
    creds = credentials_from_json(creds_json)
    drive_service = build("drive", "v3", credentials=creds)
    # Query for Google Docs mime type
    results = drive_service.files().list(
        q="mimeType='application/vnd.google-apps.document' and trashed=false",
        pageSize=200,
        fields="files(id,name,modifiedTime)"
    ).execute()
    files = results.get('files', [])
    # Return id, name, modifiedTime
    return files

def fetch_doc_text(doc_id: str, creds_json: dict) -> str:
    """
    Get raw text content from a Google Doc.
    """
    creds = credentials_from_json(creds_json)
    docs_service = build("docs", "v1", credentials=creds)
    doc = docs_service.documents().get(documentId=doc_id).execute()
    body = doc.get("body", {}).get("content", [])
    text_list = []
    for element in body:
        # paragraphs
        if 'paragraph' in element:
            for e in element['paragraph'].get('elements', []):
                text_run = e.get('textRun')
                if text_run:
                    content = text_run.get('content', '')
                    text_list.append(content)
        # tables, etc might be present - this basic approach extracts text
    return ''.join(text_list).strip()
