from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def make_pdf(report_data, filename="scan_report.pdf"):
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI VAPT SCAN REPORT</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Target:</b> {report_data['target']}", styles["Heading2"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Services & CVEs:</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    for svc in report_data["services"]:
        story.append(Paragraph(
            f"<b>Port:</b> {svc['port']} | <b>Service:</b> {svc['service']} | <b>Version:</b> {svc['version']}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 8))

        if svc["cves"]:
            for c in svc["cves"]:
                story.append(Paragraph(
                    f"• <b>{c['id']}</b> — {c['summary']}",
                    styles["Normal"]
                ))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("• No CVEs found", styles["Normal"]))

        story.append(Spacer(1, 12))

    story.append(Paragraph("<b>AI Recommendations:</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    ai_text = report_data["ai_recommendations"].replace("\n", "<br/>")
    story.append(Paragraph(ai_text, styles["Normal"]))

    doc = SimpleDocTemplate(filename, pagesize=letter)
    doc.build(story)

    print(f"[+] PDF Report Created: {filename}")
