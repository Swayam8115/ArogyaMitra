from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io


def generate_pdf(data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # Color palette
    PRIMARY    = colors.HexColor('#1B4F72')   # Dark blue
    ACCENT     = colors.HexColor('#2E86C1')   # Medium blue
    SUCCESS    = colors.HexColor('#1E8449')   # Green
    WARNING    = colors.HexColor('#B7950B')   # Amber
    DANGER     = colors.HexColor('#922B21')   # Red
    LIGHT_BG   = colors.HexColor('#EBF5FB')   # Light blue bg
    LIGHT_GRAY = colors.HexColor('#F2F3F4')
    WHITE      = colors.white

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    title_style    = style('Title',    fontSize=22, textColor=WHITE, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4)
    subtitle_style = style('Subtitle', fontSize=11, textColor=colors.HexColor('#D6EAF8'), alignment=TA_CENTER, fontName='Helvetica')
    section_style  = style('Section',  fontSize=13, textColor=PRIMARY, fontName='Helvetica-Bold', spaceBefore=14, spaceAfter=6)
    body_style     = style('Body',     fontSize=10, textColor=colors.HexColor('#2C3E50'), fontName='Helvetica', leading=16)
    small_style    = style('Small',    fontSize=9,  textColor=colors.gray, fontName='Helvetica')
    label_style    = style('Label',    fontSize=9,  textColor=WHITE, fontName='Helvetica-Bold', alignment=TA_CENTER)

    story = []

    # Header Banner
    header_data = [
        [Paragraph("ArogyaMitra", title_style)],
        [Paragraph("AI-Assisted Disease Prediction Report", subtitle_style)],
    ]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,0), PRIMARY),
        ('BACKGROUND',    (0,1), (0,1), ACCENT),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (0,0), 20),
        ('BOTTOMPADDING', (0,0), (0,0), 20),
        ('TOPPADDING',    (0,1), (0,1), 8),
        ('BOTTOMPADDING', (0,1), (0,1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # Meta Info Row 
    now = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    meta_data = [[
        Paragraph(f"<b>Date:</b> {now}", body_style),
        Paragraph(f"<b>Worker:</b> {data['workerName']}", body_style),
        Paragraph(f"<b>Location:</b> {data.get('location','—')}", body_style),
    ]]
    meta_table = Table(meta_data, colWidths=[5.6*cm, 5.6*cm, 5.8*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), LIGHT_GRAY),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Patient Information 
    story.append(Paragraph("Patient Information", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    gender  = str(data.get('patientGender') or '—').capitalize()
    age     = str(data.get('patientAge') or '—')
    patient_data = [
        [Paragraph('<b>Name</b>', body_style),    Paragraph(data['patientName'], body_style),
         Paragraph('<b>Age</b>', body_style),     Paragraph(age, body_style)],
        [Paragraph('<b>Gender</b>', body_style),  Paragraph(gender, body_style),
         Paragraph('<b>Symptoms Reported</b>', body_style), Paragraph(str(len(data['matchedSymptoms'])), body_style)],
    ]
    pt = Table(patient_data, colWidths=[3.5*cm, 5*cm, 4.5*cm, 4*cm])
    pt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), LIGHT_BG),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))

    # Primary Diagnosis 
    story.append(Paragraph("Primary Diagnosis", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    conf = data['confidenceScore']
    conf_color = SUCCESS if conf >= 75 else WARNING if conf >= 50 else DANGER
    sev = data['severityScore']
    sev_color  = DANGER if sev >= 5 else WARNING if sev >= 3 else SUCCESS

    diag_data = [
        [Paragraph('<b>Condition</b>', label_style),
         Paragraph('<b>Confidence</b>', label_style),
         Paragraph('<b>Severity Score</b>', label_style)],
        [Paragraph(data['primaryDiagnosis'], ParagraphStyle('dp', fontSize=13, fontName='Helvetica-Bold', textColor=PRIMARY, alignment=TA_CENTER)),
         Paragraph(f"{conf}%", ParagraphStyle('cp', fontSize=13, fontName='Helvetica-Bold', textColor=conf_color, alignment=TA_CENTER)),
         Paragraph(f"{sev} / 7", ParagraphStyle('sp', fontSize=13, fontName='Helvetica-Bold', textColor=sev_color, alignment=TA_CENTER))],
    ]
    dt = Table(diag_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    dt.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('BACKGROUND',    (0,1),(-1,1), LIGHT_BG),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(dt)
    story.append(Spacer(1, 8))

    # Description
    story.append(Paragraph(f"<i>{data['description']}</i>", body_style))
    story.append(Spacer(1, 14))

    # Alternative Diagnoses 
    story.append(Paragraph("Differential Diagnoses (Top 3)", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    alt_headers = [[
        Paragraph('#', label_style),
        Paragraph('Disease', label_style),
        Paragraph('Confidence (%)', label_style),
    ]]
    alt_rows = [
        [Paragraph(str(i+1), body_style),
         Paragraph(p['disease'], body_style),
         Paragraph(f"{p['confidence']}%", body_style)]
        for i, p in enumerate(data['topPredictions'])
    ]
    alt_table = Table(alt_headers + alt_rows, colWidths=[1.5*cm, 10*cm, 5.5*cm])
    alt_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('BACKGROUND',    (0,1),(-1,-1), LIGHT_GRAY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [LIGHT_BG, WHITE]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(alt_table)
    story.append(Spacer(1, 14))

    # Symptoms & Severity 
    story.append(Paragraph("Reported Symptoms & Severity", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    sev_headers = [[
        Paragraph('Symptom', label_style),
        Paragraph('Severity (1–7)', label_style),
        Paragraph('Level', label_style),
    ]]
    def sev_label(s):
        if s >= 6: return 'High'
        if s >= 3: return 'Moderate'
        return 'Low'
    def sev_row_color(s):
        if s >= 6: return colors.HexColor('#FDEDEC')
        if s >= 3: return colors.HexColor('#FEF9E7')
        return colors.HexColor('#EAFAF1')

    sev_rows = [
        [Paragraph(sv['symptom'], body_style),
         Paragraph(str(sv['severity']), body_style),
         Paragraph(sev_label(sv['severity']), body_style)]
        for sv in data['symptomSeverities']
    ]
    sev_table = Table(sev_headers + sev_rows, colWidths=[8*cm, 5*cm, 4*cm])
    row_styles = [
        ('BACKGROUND', (0, i+1), (-1, i+1), sev_row_color(data['symptomSeverities'][i]['severity']))
        for i in range(len(sev_rows))
    ]
    sev_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ] + row_styles))
    story.append(sev_table)
    story.append(Spacer(1, 14))

    # LIME Explanation 
    story.append(Paragraph("AI Explanation (LIME)", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "The following factors most influenced this prediction. "
        "Positive impact = supports the diagnosis. Negative impact = evidence against it.",
        body_style
    ))
    story.append(Spacer(1, 8))

    lime_headers = [[
        Paragraph('Feature / Symptom', label_style),
        Paragraph('Impact Score', label_style),
        Paragraph('Direction', label_style),
    ]]
    lime_rows = [
        [Paragraph(l['feature'], body_style),
         Paragraph(str(l['impact']), body_style),
         Paragraph(l['direction'], ParagraphStyle('dir', fontSize=10,
             textColor=SUCCESS if 'Supports' in l['direction'] else DANGER,
             fontName='Helvetica-Bold'))]
        for l in data['limeExplanation']
    ]
    lime_table = Table(lime_headers + lime_rows, colWidths=[8*cm, 4.5*cm, 4.5*cm])
    lime_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), PRIMARY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [LIGHT_BG, WHITE]),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#AED6F1')),
    ]))
    story.append(lime_table)
    story.append(Spacer(1, 14))

    # Clinical Conclusion (LLM) 
    story.append(Paragraph("Clinical Decision Support Summary", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    llm = data.get("llmConclusion", {})

    story.append(Paragraph("Diagnosis Summary", section_style))
    story.append(Paragraph(llm.get("diagnosis_summary", ""), body_style))

    story.append(Paragraph("Confidence Interpretation", section_style))
    story.append(Paragraph(llm.get("confidence_interpretation", ""), body_style))

    story.append(Paragraph("Severity Assessment", section_style))
    story.append(Paragraph(llm.get("severity_assessment", ""), body_style))

    story.append(Paragraph("Recommended Next Steps", section_style))
    story.append(Paragraph(llm.get("recommended_next_steps", ""), body_style))

    story.append(Paragraph("Referral Recommendation", section_style))
    story.append(Paragraph(llm.get("referral_recommendation", ""), body_style))

    # Precautions 
    story.append(KeepTogether([
        Paragraph("Recommended Precautions", section_style),
        HRFlowable(width="100%", thickness=1, color=ACCENT),
        Spacer(1, 8),
    ]))
    for i, p in enumerate(data['precautions'], 1):
        story.append(Paragraph(f"&nbsp;&nbsp;{i}.  {p.capitalize()}", body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 14))

    # Disclaimer 
    disclaimer_data = [[Paragraph(
        "⚠️  <b>Disclaimer:</b> This report is AI-generated for decision support only. "
        "It does not replace a qualified doctor's diagnosis. If the healthcare worker is not confident "
        "in this result, please escalate to a doctor for a second opinion.",
        ParagraphStyle('disc', fontSize=9, textColor=colors.HexColor('#7D6608'),
                       fontName='Helvetica', leading=14)
    )]]
    disc_table = Table(disclaimer_data, colWidths=[17*cm])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), colors.HexColor('#FEF9E7')),
        ('BOX',           (0,0),(-1,-1), 1, colors.HexColor('#F0B27A')),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('LEFTPADDING',   (0,0),(-1,-1), 12),
        ('RIGHTPADDING',  (0,0),(-1,-1), 12),
    ]))
    story.append(disc_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()