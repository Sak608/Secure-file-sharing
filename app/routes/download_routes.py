from flask import Blueprint, request, send_file, abort
from app.models import File
from cryptography.fernet import Fernet
from app.utils.crypto_util import fernet
from datetime import datetime


bp = Blueprint('download', __name__)

# Use the same key used during encryption
# fernet_key = Fernet.generate_key()
# fernet = Fernet(fernet_key)

import os

with open("secret.key", "rb") as key_file:
    fernet_key = key_file.read()

fernet = Fernet(fernet_key)


@bp.route('/download/<token>')
def download_file(token):
    file_entry = File.query.filter_by(token=token).first()

    if not file_entry:
        return abort(404, description="Invalid or expired token")
    if datetime.utcnow() > file_entry.expiry_time:
        return abort(403, description="Link has expired")

    try:
        with open(file_entry.filepath, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)

        # Send decrypted file
        return send_file(
            io.BytesIO(decrypted_data),
            download_name=file_entry.filename,
            as_attachment=True
        )

    except Exception as e:
        return abort(500, description="Failed to decrypt or send file")
import io