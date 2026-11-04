import os
import io
from flask import Flask, render_template, request, jsonify, send_file, session
from dotenv import load_dotenv

from resume_parser import extract_resume_text
from tailor_engine import tailor_resume_and_letter, recommend_companies_for_student, tune_bullet
from docx_generator import create_jakes_resume_docx, create_application_letter_docx
from pdf_generator import create_jakes_resume_pdf, create_application_letter_pdf
from tracker import (
    init_db,
    save_application,
    get_all_applications,
    get_application,
    update_application_status,
    delete_application
)

load_dotenv()
init_db()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "resumez-super-secret-key-2026")

# In-memory storage cache for the active session (fallback if cookies exceed limit)
SESSION_DATA_CACHE = {}


def get_active_data(sid: str = None) -> dict:
    if sid and sid in SESSION_DATA_CACHE:
        return SESSION_DATA_CACHE[sid]
    return session.get("tailored_data") or {}


@app.route("/")
def index():
    return render_template("index.html")


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.route("/api/upload-resume", methods=["POST"])
def api_upload_resume():
    if "resume_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["resume_file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        text = extract_resume_text(file)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": f"Failed to extract resume text: {str(e)}"}), 500


@app.route("/api/recommend-companies", methods=["POST"])
def api_recommend_companies():
    data = request.get_json() or {}
    resume_text = data.get("resume_text", "").strip()
    target_location = data.get("target_location", "Any")

    if not resume_text:
        return jsonify({"error": "Resume text is required"}), 400

    try:
        recs = recommend_companies_for_student(
            resume_text=resume_text,
            target_location=target_location
        )
        return jsonify({"recommendations": recs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tailor", methods=["POST"])
def api_tailor():
    data = request.get_json() or {}
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    company_name = data.get("company_name", "").strip()
    role_title = data.get("role_title", "").strip()
    location = data.get("location", "").strip()
    career_level = data.get("career_level", "student")

    if not resume_text or not job_description:
        return jsonify({"error": "Both resume profile and job description are required"}), 400

    try:
        tailored = tailor_resume_and_letter(
            resume_text=resume_text,
            job_description=job_description,
            company_name=company_name,
            role_title=role_title,
            location=location,
            career_level=career_level
        )

        # Save to SQLite Tracker
        match_score = tailored.get("ats_assessment", {}).get("match_score", 90)
        saved_id = save_application(
            company_name=company_name,
            role_title=role_title,
            location=location,
            match_score=match_score,
            data=tailored,
            status="Draft",
            career_level=career_level
        )

        # Store in session and cache
        session_id = session.get("sid") or os.urandom(16).hex()
        session["sid"] = session_id
        session["active_saved_id"] = saved_id
        SESSION_DATA_CACHE[session_id] = tailored

        return jsonify({
            "tailored_data": tailored,
            "saved_id": saved_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tune-bullet", methods=["POST"])
def api_tune_bullet():
    data = request.get_json() or {}
    bullet_text = data.get("bullet_text", "").strip()
    mode = data.get("mode", "add_metrics")
    target_role = data.get("target_role", "Software Engineer")

    if not bullet_text:
        return jsonify({"error": "Bullet text is required"}), 400

    try:
        refined = tune_bullet(
            bullet_text=bullet_text,
            mode=mode,
            target_role=target_role
        )
        return jsonify({"tuned_bullet": refined})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications", methods=["GET"])
def api_get_applications():
    apps = get_all_applications()
    return jsonify({"applications": apps})


@app.route("/api/applications/<int:app_id>", methods=["GET"])
def api_get_application(app_id):
    app_record = get_application(app_id)
    if not app_record:
        return jsonify({"error": "Application not found"}), 404

    # Update active session
    session_id = session.get("sid") or os.urandom(16).hex()
    session["sid"] = session_id
    session["active_saved_id"] = app_id
    SESSION_DATA_CACHE[session_id] = app_record.get("data", {})

    return jsonify(app_record)


@app.route("/api/applications/<int:app_id>/status", methods=["POST"])
def api_update_status(app_id):
    data = request.get_json() or {}
    status = data.get("status", "Draft")
    update_application_status(app_id, status)
    return jsonify({"success": True, "status": status})


@app.route("/api/applications/<int:app_id>", methods=["DELETE"])
def api_delete_application(app_id):
    delete_application(app_id)
    return jsonify({"success": True})


# ==============================================================================
# DOWNLOAD & PREVIEW ENDPOINTS
# ==============================================================================

@app.route("/preview/resume/pdf", methods=["GET"])
def preview_resume_pdf():
    sid = session.get("sid")
    data = get_active_data(sid)
    if not data:
        # Fallback to last saved application in DB
        apps = get_all_applications()
        if apps:
            last = get_application(apps[0]["id"])
            if last and last.get("data"):
                data = last["data"]

    if not data:
        return "No resume data available", 404

    buffer = create_jakes_resume_pdf(data)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False
    )


@app.route("/download/resume/docx", methods=["GET"])
def download_resume_docx():
    sid = session.get("sid")
    data = get_active_data(sid)
    if not data:
        return "No resume data available", 404

    name = data.get("personal_info", {}).get("name", "Candidate").replace(" ", "_")
    company = data.get("ats_assessment", {}).get("target_company", "Company").replace(" ", "_")
    filename = f"{name}_{company}_Resume.docx"

    buffer = create_jakes_resume_docx(data)
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=filename
    )


@app.route("/download/resume/pdf", methods=["GET"])
def download_resume_pdf():
    sid = session.get("sid")
    data = get_active_data(sid)
    if not data:
        return "No resume data available", 404

    name = data.get("personal_info", {}).get("name", "Candidate").replace(" ", "_")
    company = data.get("ats_assessment", {}).get("target_company", "Company").replace(" ", "_")
    filename = f"{name}_{company}_Resume.pdf"

    buffer = create_jakes_resume_pdf(data)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


@app.route("/download/letter/docx", methods=["GET"])
def download_letter_docx():
    sid = session.get("sid")
    data = get_active_data(sid)
    if not data:
        return "No cover letter data available", 404

    name = data.get("personal_info", {}).get("name", "Candidate").replace(" ", "_")
    company = data.get("ats_assessment", {}).get("target_company", "Company").replace(" ", "_")
    filename = f"{name}_{company}_Letter.docx"

    buffer = create_application_letter_docx(data)
    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=filename
    )


@app.route("/download/letter/pdf", methods=["GET"])
def download_letter_pdf():
    sid = session.get("sid")
    data = get_active_data(sid)
    if not data:
        return "No cover letter data available", 404

    name = data.get("personal_info", {}).get("name", "Candidate").replace(" ", "_")
    company = data.get("ats_assessment", {}).get("target_company", "Company").replace(" ", "_")
    filename = f"{name}_{company}_Letter.pdf"

    buffer = create_application_letter_pdf(data)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Flask server on http://localhost:{port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
