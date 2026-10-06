import io
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models import SentimentResult

COLUMNS = ["Review", "Sentiment", "Confidence (%)", "Prediction Date"]


def _safe(text):
    """Stop spreadsheet formula injection (cells starting with = + - @)."""
    return "'" + text if text and text[0] in "=+-@" else text


def build_dataframe(user):
    """Admins get every result, normal users only their own."""
    query = SentimentResult.query.order_by(SentimentResult.prediction_date.desc())
    if user.role != "admin":
        query = query.filter(SentimentResult.user_id == user.id)
    rows = [
        {
            "Review": _safe(r.text),
            "Sentiment": r.sentiment,
            "Confidence (%)": r.confidence_score,
            "Prediction Date": r.prediction_date.strftime("%Y-%m-%d %H:%M"),
        }
        for r in query.all()
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sentiment Report")
    return buffer.getvalue()


def to_pdf_bytes(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), title="Sentiment Report")
    styles = getSampleStyleSheet()
    story = [Paragraph("Sentiment Analysis Report", styles["Title"]), Spacer(1, 12)]

    if df.empty:
        story.append(Paragraph("No predictions found.", styles["Normal"]))
    else:
        cell = styles["BodyText"]
        data = [COLUMNS]
        for _, row in df.iterrows():
            review = row["Review"] if len(row["Review"]) <= 300 else row["Review"][:300] + "..."
            data.append([
                Paragraph(escape(review), cell),
                row["Sentiment"],
                f'{row["Confidence (%)"]:.2f}',
                row["Prediction Date"],
            ])
        table = Table(data, colWidths=[400, 80, 90, 110], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b5bdb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
    doc.build(story)
    return buffer.getvalue()
