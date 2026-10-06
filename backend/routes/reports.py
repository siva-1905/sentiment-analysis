import io

from flask import Blueprint, send_file
from flask_login import current_user, login_required

from services import report_service
from services.audit_service import log_action

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _send(data, mimetype, filename, label):
    log_action("Report Download", f"Downloaded {label} report")
    return send_file(io.BytesIO(data), mimetype=mimetype, as_attachment=True, download_name=filename)


@reports_bp.get("/csv")
@login_required
def csv_report():
    data = report_service.to_csv_bytes(report_service.build_dataframe(current_user))
    return _send(data, "text/csv", "sentiment_report.csv", "CSV")


@reports_bp.get("/excel")
@login_required
def excel_report():
    data = report_service.to_excel_bytes(report_service.build_dataframe(current_user))
    return _send(
        data,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "sentiment_report.xlsx",
        "Excel",
    )


@reports_bp.get("/pdf")
@login_required
def pdf_report():
    data = report_service.to_pdf_bytes(report_service.build_dataframe(current_user))
    return _send(data, "application/pdf", "sentiment_report.pdf", "PDF")
