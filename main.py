import uvicorn
import re
import os
from typing import List, Tuple

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload directory exists


def parse_headers(headers: bytes) -> Tuple[str, str]:
    """Extract filename and content type from multipart headers."""
    headers_str = headers.decode()

    filename_match = re.search(r'filename="(.+?)"', headers_str)
    filename = filename_match.group(1) if filename_match else "uploaded_file.bin"

    content_type_match = re.search(r'Content-Type: (.+)', headers_str)
    content_type = content_type_match.group(1).strip() if content_type_match else "application/octet-stream"

    return filename, content_type


async def app(scope, receive, send):
    assert scope["type"] == "http"

    # Get headers to detect boundary
    headers = dict(scope.get("headers", []))
    content_type = headers.get(b"content-type", b"").decode()

    # Extract boundary
    boundary_match = re.search(r"boundary=(.+)", content_type)
    boundary = boundary_match.group(1) if boundary_match else None
    if not boundary:
        await send({"type": "http.response.start", "status": 400, "headers": [[b"content-type", b"text/plain"]]})
        await send({"type": "http.response.body", "body": b"Invalid multipart form-data"})
        return

    boundary_bytes = f"--{boundary}".encode()

    # Read request body in chunks
    body = b""
    while True:
        event = await receive()
        print('Receiving...')
        body += event.get("body", b"")
        if not event.get("more_body", False):
            break

    # Split body by boundary
    parts = body.split(boundary_bytes)

    for part in parts:
        part = part.strip()
        if not part or part == b"--":  # Skip empty parts
            continue

        headers_end = part.find(b"\r\n\r\n")
        if headers_end == -1:
            continue

        headers_section = part[:headers_end]
        content_section = part[headers_end + 4:]  # Skip \r\n\r\n

        filename, content_type = parse_headers(headers_section)

        # Save file
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(content_section)

        print(f"Saved file: {file_path} (Type: {content_type})")

    # Send response
    await send({"type": "http.response.start", "status": 200, "headers": [[b"content-type", b"text/plain"]]})
    await send({"type": "http.response.body", "body": b"File uploaded successfully!"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
