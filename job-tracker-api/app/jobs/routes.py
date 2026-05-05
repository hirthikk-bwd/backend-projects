from flask import request, jsonify
from . import jobs_bp
from app import db
from app.models import JobApplication
from flask_jwt_extended import jwt_required, get_jwt_identity


@jobs_bp.route("/", methods=["GET"])
@jwt_required()
def get_jobs():
    user_id = get_jwt_identity()
    jobs = JobApplication.query.filter_by(user_id=user_id).all()
    return (
        jsonify(
            [
                {
                    "id": job.id,
                    "company": job.company,
                    "role": job.role,
                    "status": job.status,
                    "notes": job.notes,
                }
                for job in jobs
            ]
        ),
        200,
    )


@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def create_job():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get("company") or not data.get("role"):
        return jsonify({"error": "Company and role required"}), 400

    job = JobApplication(
        user_id=user_id,
        company=data.get("company"),
        role=data.get("role"),
        status=data.get("status", "applied"),
        notes=data.get("notes", ""),
    )
    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job added", "id": job.id}), 201


@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    user_id = get_jwt_identity()
    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    data = request.get_json()
    job.company = data.get("company", job.company)
    job.role = data.get("role", job.role)
    job.status = data.get("status", job.status)
    job.notes = data.get("notes", job.notes)

    db.session.commit()
    return jsonify({"message": "Job updated"}), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    user_id = get_jwt_identity()
    job = JobApplication.query.filter_by(id=job_id, user_id=user_id).first()

    if not job:
        return jsonify({"error": "Job not found"}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"}), 200
