from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, File
import os, uuid
from cryptography.fernet import Fernet
from app.utils.crypto_util import fernet
import qrcode

bp = Blueprint('upload', __name__)

allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash("No file selected", "danger")
            return redirect(url_for('upload.dashboard'))

        uploaded_file = request.files['file']

        if not allowed_file(uploaded_file.filename):
            flash("Invalid file type", "warning")
            return redirect(url_for('upload.dashboard'))

        filename = secure_filename(uploaded_file.filename)
        token = str(uuid.uuid4())
        encrypted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{token}.enc")

        # Encrypt and save
        data = uploaded_file.read()
        encrypted_data = fernet.encrypt(data)
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)

        # Save file info in DB
        file_entry = File(filename=filename, filepath=encrypted_path, token=token, user_id=current_user.id)
        db.session.add(file_entry)
        db.session.commit()

        # ✅ Generate secure download URL
        download_url = url_for('download.download_file', token=token, _external=True)

        # ✅ Generate and save QR code in static folder
        qr = qrcode.make(download_url)
        qr_path = os.path.join(current_app.static_folder, f"qr_{token}.png")
        qr.save(qr_path)

        # ✅ Render download link + QR code page
        return render_template("link_shared.html", token=token)

    # GET method — show dashboard with file list
    user_files = File.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", files=user_files)
