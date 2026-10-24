import json, sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
_F='/usr/share/fonts/truetype/liberation/'
for n,f in [('LS','LiberationSans-Regular'),('LS-B','LiberationSans-Bold'),('LS-I','LiberationSans-Italic'),('LT','LiberationSerif-Regular'),('LT-B','LiberationSerif-Bold'),('LT-I','LiberationSerif-Italic')]:
    pdfmetrics.registerFont(TTFont(n,_F+f+'.ttf'))

OUT_PDF, OUT_JSON = sys.argv[1], sys.argv[2]
W, H = letter; M = 54
INK = HexColor('#1a1a1a'); GREY = HexColor('#666666'); RULE = HexColor('#bbbbbb'); TINT = HexColor('#f3f3f1')
c = canvas.Canvas(OUT_PDF, pagesize=letter)
c.setTitle('Alvarez v. Sunline Freight - case file (sample)'); c.setAuthor('CaseEdge sample data')
KEYS = {}; META = []; BILLS = {}
pageno = [0]

def hl(key, x, y, w, h):
    KEYS.setdefault(key, {'page': pageno[0], 'rects': [], 'label': META[-1]['label']})
    KEYS[key]['rects'].append([round(x,1), round(y,1), round(w,1), round(h,1)])

def footer(bates, label):
    c.setStrokeColor(RULE); c.setLineWidth(.5); c.line(M, 46, W-M, 46)
    c.setFont('LS', 7); c.setFillColor(GREY)
    c.drawString(M, 34, 'SAMPLE RECORD · FICTIONAL PATIENT · FOR DEMONSTRATION ONLY')
    c.drawCentredString(W/2, 22, label); c.drawRightString(W-M, 34, bates)

def begin(ex, pg, fac, doc):
    pageno[0] += 1
    META.append({'label': f'Ex. {ex}, p. {pg}' if ex else 'Index', 'ex': ex, 'pg': pg, 'fac': fac, 'doc': doc})

def end(ex, pg):
    footer(f'ALVAREZ-EX{ex}-{pg:04d}' if ex else 'ALVAREZ-0000', META[-1]['label']); c.showPage()

def header(name, sub, doc, pg, of, bold='LS-B'):
    c.setFillColor(INK); c.setFont(bold, 14); c.drawString(M, H-66, name)
    c.setFont('LS', 7.5); c.setFillColor(GREY); c.drawString(M, H-80, sub)
    c.setFillColor(INK); c.setFont('LS-B', 8.5); c.drawRightString(W-M, H-66, doc)
    c.setFont('LS', 7.5); c.setFillColor(GREY); c.drawRightString(W-M, H-80, f'Page {pg} of {of}')
    c.setStrokeColor(INK); c.setLineWidth(1); c.line(M, H-90, W-M, H-90)

def fields(rows, y):
    c.setFont('LS', 8)
    for r in rows:
        x = M
        for k, v in r:
            c.setFillColor(GREY); c.drawString(x, y, k.upper()); c.setFillColor(INK); c.drawString(x, y-11, v); x += 170
        y -= 28
    c.setStrokeColor(RULE); c.setLineWidth(.5); c.line(M, y+6, W-M, y+6)
    return y - 14

def body(sections, y, font='LS', fs=9.8):
    lh = fs*1.45
    for head, paras in sections:
        if head:
            c.setFont('LS-B', 8); c.setFillColor(INK); c.drawString(M, y, head.upper()); y -= 15
        for text, key in paras:
            c.setFont(font, fs); c.setFillColor(INK)
            for ln in simpleSplit(text, font, fs, W-2*M):
                c.drawString(M, y, ln)
                if key: hl(key, M-1, y-fs*0.28, stringWidth(ln, font, fs)+2, fs*1.22)
                y -= lh
            y -= 5
        y -= 8
    return y

PATIENT = [('Patient','ALVAREZ, MARIA'),('DOB','06/02/1988'),('Sex','F')]
FAC = {
 'avmc':('Arlington Valley Medical Center','Emergency Department · 2100 Arlington Valley Rd, Riverside, CA 92505 · (951) 555-0142','AVM-0418832','LS'),
 'sso':('Sycamore Spine & Orthopedics','James Rhee, MD · 780 Sycamore Ct, Suite 200, Riverside, CA 92507 · (951) 555-0177','SSO-22917','LT'),
 'cri':('Canyon Ridge Imaging','Diagnostic Radiology · 3155 Canyon Ridge Dr, Riverside, CA 92506 · (951) 555-0110','CRI-770214','LS'),
 'hpt':('Halden Physical Therapy','4410 Halden Ave, Riverside, CA 92503 · (951) 555-0163','HPT-5531','LS'),
 'npi':('Northgate Pain Institute','Interventional Pain Medicine · 615 Northgate Blvd, Riverside, CA 92504 · (951) 555-0188','NPI-10388','LT'),
 'vcu':('Valley Crossroads Urgent Care','1290 Crossroads Pkwy, Riverside, CA 92508 · (951) 555-0121','VCU-88412','LS'),
}

def record(ex, pg, of, fac, doc, dos, prov, sections, sign, mrn_override=None):
    name, sub, mrn, font = FAC[fac]
    begin(ex, pg, name, doc.title())
    header(name, sub, doc, pg, of, 'LS-B' if font=='LS' else 'LT-B')
    y = fields([PATIENT, [('MRN', mrn_override or mrn), ('Date of service', dos), ('Provider', prov)]], H-108)
    y = body(sections, y, font, 10.5 if font=='LT' else 9.8)
    c.setFont('LS-I', 8.5); c.setFillColor(GREY); c.drawString(M, y-6, sign)
    end(ex, pg)

def letterpage(ex, pg, org, sub, doc, date, to, re_lines, paras, sign):
    begin(ex, pg, org, doc)
    c.setFillColor(INK); c.setFont('LT-B', 15); c.drawString(M, H-70, org)
    c.setFont('LS', 7.5); c.setFillColor(GREY); c.drawString(M, H-84, sub)
    c.setStrokeColor(INK); c.setLineWidth(.8); c.line(M, H-94, W-M, H-94)
    y = H-128; c.setFont('LT', 11); c.setFillColor(INK)
    c.drawString(M, y, date); y -= 26
    for ln in to: c.drawString(M, y, ln); y -= 14
    y -= 10
    for ln in re_lines: c.setFont('LT-B', 11); c.drawString(M, y, ln); y -= 14
    y -= 12
    y = body([(None, paras)], y, 'LT', 11)
    c.setFont('LT', 11); c.drawString(M, y-4, 'Sincerely,'); c.drawString(M, y-40, sign[0])
    c.setFont('LT-I', 10); c.setFillColor(GREY); c.drawString(M, y-54, sign[1])
    end(ex, pg)

def money(v): return f'{v:,.2f}'

def bill(ex, pg, of, fac, prov_key, acct, lines, pay, adj, paydate, note):
    name, sub, mrn, font = FAC[fac]
    begin(ex, pg, name, 'Itemized statement')
    header(name, sub, 'ITEMIZED STATEMENT', pg, of)
    y = fields([PATIENT, [('Account', acct), ('Statement date', '10/01/2026'), ('Guarantor', 'ALVAREZ, MARIA')]], H-108)
    cols = [M, M+72, M+150, W-M-92, W-M]
    c.setFont('LS-B', 7.5); c.setFillColor(INK)
    c.drawString(cols[0], y, 'DATE'); c.drawString(cols[1], y, 'CODE'); c.drawString(cols[2], y, 'DESCRIPTION')
    c.drawRightString(cols[3], y, 'UNITS'); c.drawRightString(cols[4], y, 'CHARGE')
    c.setStrokeColor(RULE); c.line(M, y-5, W-M, y-5); y -= 18
    total = 0
    c.setFont('LS', 8.6)
    for dos, code, desc, units, amt in lines:
        c.setFillColor(INK)
        c.drawString(cols[0], y, dos); c.drawString(cols[1], y, code); c.drawString(cols[2], y, desc)
        c.drawRightString(cols[3], y, str(units)); c.drawRightString(cols[4], y, money(amt))
        if prov_key == 'ex10p2': hl(prov_key, M-2, y-3.5, W-2*M+4, 12)
        total += amt; y -= 15
    c.setStrokeColor(RULE); c.line(M, y+4, W-M, y+4); y -= 14
    bal = total - pay - adj
    rows = [('Total charges', money(total)), (f'Payments · health plan {paydate}' if pay else 'Payments', ('-' if pay else '')+money(pay)),
            ('Contractual adjustments', ('-' if adj else '')+money(adj))]
    x0 = W-M-250
    c.setFont('LS', 8.8)
    for k, v in rows:
        c.drawString(x0, y, k); c.drawRightString(W-M, y, v); y -= 15
    c.setStrokeColor(INK); c.line(x0, y+9, W-M, y+9)
    c.setFont('LS-B', 9.5); c.drawString(x0, y-4, 'BALANCE DUE'); c.drawRightString(W-M, y-4, money(bal))
    hl(prov_key, x0-3, y-8, W-M-x0+6, 14)
    y -= 34
    if note:
        c.setFont('LS-I', 8.5); c.setFillColor(GREY)
        for ln in simpleSplit(note, 'LS-I', 8.5, W-2*M): c.drawString(M, y, ln); y -= 12
    BILLS[prov_key] = {'lines': [[d, cd, ds, u, a] for d, cd, ds, u, a in lines], 'total': total, 'paid': pay, 'adj': adj, 'balance': bal}
    end(ex, pg)

# ---------- Cover index (filled after) ----------
INDEX = [
 ('1','Inland Valley Traffic Division','Traffic collision report'),('2','Arlington Valley Medical Center','Emergency department records'),
 ('3','Canyon Ridge Imaging','MRI reports'),('4','Sycamore Spine & Orthopedics','Orthopedic records'),
 ('5','Halden Physical Therapy','Physical therapy records'),('6','Northgate Pain Institute','Procedure notes'),
 ('7','Riverside Community Pharmacy','Dispensing history'),('8','Valley Crossroads Urgent Care','Prior records (2019)'),('9','Westbridge Indemnity Company','Policy limits letter'),
 ('10','Providers','Itemized statements'),('11','Brightline Family Dental','Wage verification'),
 ('12','Lienholders','Lien and reimbursement notices'),('13','Reyes & Lin LLP','Evidence preservation letter'),
]
begin(0, 0, 'CaseEdge', 'Case file index')
c.setFillColor(INK); c.setFont('LS-B', 16); c.drawString(M, H-96, 'CASE FILE · CITED PAGES')
c.setFont('LS', 11); c.drawString(M, H-116, 'Alvarez v. Sunline Freight, LLC · Matter 2026-0147')
c.setFillColor(GREY); c.setFont('LS', 9); c.drawString(M, H-134, 'Every page cited in the chronology, case signals, ledger and demand, excerpted from the full exhibits.')
y = H-176; c.setFillColor(INK); c.setFont('LS-B', 8.5)
c.drawString(M, y, 'EXHIBIT'); c.drawString(M+60, y, 'SOURCE'); c.drawString(M+290, y, 'DOCUMENT')
c.setStrokeColor(RULE); c.line(M, y-6, W-M, y-6); y -= 22; c.setFont('LS', 9.5)
for ex, src, doc in INDEX:
    c.drawString(M, y, f'Ex. {ex}'); c.drawString(M+60, y, src); c.drawString(M+290, y, doc); y -= 18
end(0, 0)

# ---------- Ex. 1 Police report ----------
begin(1, 3, 'Inland Valley Traffic Division', 'Traffic collision report')
header('Inland Valley Traffic Division', 'Collision Investigation Unit · 4000 Orange St, Riverside, CA 92501 · (951) 555-0100', 'TRAFFIC COLLISION REPORT · NARRATIVE', 3, 9)
y = fields([[('Report no.','IVT-26-03-1147'),('Date / time','03/14/2026 14:21'),('Location','I-215 N at Box Springs Rd')],
            [('Party 1 (D1)','R. Haines · Sunline Freight, LLC'),('Party 2 (D2)','Maria Alvarez'),('Officer','Ofc. T. Duarte #4471')]], H-108)
y = body([
 ('Summary', [('V2 was stopped in the No. 2 lane for slowing traffic.', None),
              ('V1, a commercial tractor-trailer, failed to slow for stopped traffic and struck the rear of V2.', 'ex1p3')]),
 ('Statements', [('D2 stated she had been stopped for several seconds when she was struck from behind and felt pain in her neck and lower back.', None),
                 ('D1 stated he looked down at his dispatch tablet and did not see traffic stop.', 'ex1p3')]),
 ('Findings', [('Primary collision factor: CVC 21703, following too closely. Party at fault: D1.', 'ex1p3'),
               ('D2 transported by ambulance to Arlington Valley Medical Center.', None)]),
], y)
end(1, 3)

# ---------- Ex. 2 ED ----------
record(2, 14, 22, 'avmc', 'ED PHYSICIAN NOTE', '03/14/2026', 'K. Moreno, MD', [
 ('Chief complaint', [('Neck pain and low back pain after motor vehicle collision.', None)]),
 ('History of present illness', [('38 y/o F, restrained driver, rear-ended by a tractor-trailer while stopped in traffic on I-215 N. Airbags did not deploy. Arrived by ambulance in cervical collar.', 'ex2p14m'),
     ('Reports neck and low back pain 7/10 with tingling down the left leg.', 'ex2p14'),
     ('No loss of consciousness. Denies head strike, chest pain or abdominal pain.', None)]),
 ('Physical exam', [('Cervical paraspinal tenderness without midline step-off. Lumbar paraspinal tenderness, left greater than right. Strength 5/5 in both lower extremities. Patient reports decreased sensation over the left lateral calf.', None)]),
 ('Plan', [('CT cervical spine without contrast per NEXUS criteria.', None), ('Ketorolac 15 mg IM given for pain. Reassess after imaging.', 'ex2p14k')]),
], 'Electronically signed by K. Moreno, MD · 03/14/2026 16:40')
record(2, 21, 22, 'avmc', 'ED DISPOSITION SUMMARY', '03/14/2026', 'K. Moreno, MD', [
 ('Imaging results', [('CT cervical spine without contrast: no acute fracture or malalignment. Prevertebral soft tissues normal.', None)]),
 ('Disposition', [('Discharged home in stable condition with diagnoses of cervical sprain (S13.4XXA) and lumbar strain (S39.012A).', 'ex2p21')]),
 ('Medications', [('Cyclobenzaprine 5 mg PO TID as needed for spasm. Ibuprofen 600 mg PO every 8 hours with food.', 'ex2p21m')]),
 ('Follow-up and work', [('Follow up with orthopedics within one week.', None), ('Off work through 03/17/2026.', 'ex2p21w')]),
], 'Electronically signed by K. Moreno, MD · 03/14/2026 18:05')

# ---------- Ex. 3 MRI ----------
record(3, 42, 44, 'cri', 'MRI LUMBAR SPINE WITHOUT CONTRAST', '04/02/2026', 'A. Lindqvist, MD', [
 ('Indication', [('Low back pain with left leg radiation after motor vehicle collision on 03/14/2026.', None)]),
 ('Findings', [('L3-L4: No disc herniation, canal or foraminal stenosis.', None),
     ('L4-L5: 5 mm posterior disc protrusion with mass effect on the traversing left L5 nerve root.', 'ex3p42'),
     ('L5-S1: Mild facet arthropathy. No canal stenosis.', None)]),
 ('Impression', [('1. L4-L5 posterior disc protrusion contacting and displacing the left L5 nerve root.', None), ('2. No fracture or acute marrow abnormality.', None),
     ('Cervical MRI performed the same day is reported separately (p. 43).', None)]),
], 'Interpreted by A. Lindqvist, MD · 04/02/2026 11:12')

# ---------- Ex. 4 Ortho ----------
record(4, 103, 137, 'sso', 'ORTHOPEDIC CONSULTATION', '03/18/2026', 'James Rhee, MD', [
 ('History', [('Patient seen for low back pain radiating to the left calf since a motor vehicle collision on 03/14/2026. Pain worse with sitting and bending.', 'ex4p103c')]),
 ('Examination', [('Lumbar flexion limited to 40 degrees by pain.', None),
     ('Straight-leg raise positive on the left at 40 degrees; negative on the right.', 'ex4p103'),
     ('Diminished light-touch sensation in the left L5 dermatome. Reflexes symmetric.', None)]),
 ('Assessment', [('Lumbar radiculopathy, left (M54.16). Cervicalgia (M54.2).', None)]),
 ('Plan', [('MRI lumbar and cervical spine without contrast. Physical therapy three times per week. Lumbar orthosis dispensed.', None),
     ('Work status: modified duty, no lifting over 10 lb, until re-evaluated.', 'ex4p103w')]),
], 'James Rhee, MD · Board certified, orthopedic surgery')
record(4, 119, 137, 'sso', 'ORTHOPEDIC FOLLOW-UP', '06/12/2026', 'James Rhee, MD', [
 ('Interval history', [('Returns after six weeks without care due to family obligations.', None),
     ('Low back pain 6/10, left L5 radicular symptoms persist.', 'ex4p119')]),
 ('Examination', [('Straight-leg raise positive on the left at 45 degrees. Strength 5-/5 left extensor hallucis longus.', None)]),
 ('Plan', [('Repeat transforaminal injection. Discussed surgical and non-surgical options. Follow up in eight weeks.', None), ('Work status: modified duty continues.', 'ex4p119w')]),
], 'James Rhee, MD')
record(4, 135, 137, 'sso', 'SURGICAL CONSULTATION', '08/20/2026', 'James Rhee, MD', [
 ('History', [('Five months of conservative care including physical therapy and two transforaminal injections, with only temporary relief.', None)]),
 ('Assessment', [('Persistent left L5 radiculopathy from L4-L5 disc protrusion, refractory to conservative treatment.', None)]),
 ('Recommendation', [('Recommend left L4-L5 microdiscectomy.', 'ex4p135'),
     ('Estimated cost of surgery including facility, surgeon and anesthesia: $98,000.', 'ex4p135'),
     ('Risks, benefits and alternatives discussed. Patient wishes to proceed when cleared.', 'ex4p135p')]),
 ('Causation', [('Within reasonable medical probability, the L4-L5 injury and the need for surgery are the result of the motor vehicle collision of 03/14/2026.', 'ex4p135c')]),
], 'James Rhee, MD · 08/20/2026')

# ---------- Ex. 5 PT ----------
record(5, 3, 144, 'hpt', 'PHYSICAL THERAPY INITIAL EVALUATION', '03/24/2026', 'L. Ortega, DPT', [
 ('Referral', [('Referred by James Rhee, MD for neck and low back injuries from a motor vehicle collision on 03/14/2026.', 'ex5p3c')]),
 ('Subjective', [('Patient unable to sit longer than 20 minutes or lift a laundry basket.', 'ex5p3')]),
 ('Objective', [('Oswestry Disability Index 46% (severe disability). Lumbar flexion 45 degrees with guarded movement.', 'ex5p3')]),
 ('Plan', [('Therapeutic exercise and manual therapy, 3x/week for 12 weeks.', None)]),
], 'L. Ortega, DPT · 03/24/2026')
record(5, 61, 144, 'hpt', 'PHYSICAL THERAPY PROGRESS NOTE · VISIT 18', '05/02/2026', 'L. Ortega, DPT', [
 ('Subjective', [('Patient reports gradual improvement in sitting tolerance. Continues to feel tingling in the left calf by end of day.', None),
     ('Patient reports she will miss upcoming visits because she has no childcare for her two children.', 'ex5p61')]),
 ('Objective', [('Oswestry Disability Index 38% (previous 46%). Lumbar flexion 55 degrees.', None)]),
 ('Plan', [('Home exercise program reviewed and provided in writing to continue during absence. Resume 3x/week when able.', None)]),
], 'L. Ortega, DPT · 05/02/2026')
record(5, 62, 144, 'hpt', 'ATTENDANCE LOG', '03/24/2026 - 09/30/2026', 'Front desk', [
 ('Summary', [('Scheduled: 54 visits. Attended: 36. Cancelled by patient: 17. No-show: 1.', None)]),
 ('Cancellations', [('05/04/2026 - 06/10/2026: 17 visits cancelled by patient. Reason given: no childcare for her two children.', 'ex5p62'),
     ('Patient called 06/11/2026 to resume; first visit back 06/15/2026.', None)]),
 ('No-shows', [('08/11/2026: no-show. No reason recorded. Rescheduled to 08/13/2026 and attended.', 'ex5p62n')]),
], 'Halden Physical Therapy · front desk record')
record(5, 140, 144, 'hpt', 'PHYSICAL THERAPY DISCHARGE SUMMARY', '09/30/2026', 'L. Ortega, DPT', [
 ('Summary', [('Patient discharged after 36 visits; progress has plateaued.', 'ex5p140'),
     ('Oswestry Disability Index 34% at discharge. Patient continues to require assistance with lifting.', None)]),
 ('Recommendation', [('Continue home exercise program. Follow up with orthopedic surgeon regarding surgical plan.', None)]),
], 'L. Ortega, DPT · 09/30/2026')

# ---------- Ex. 6 Pain ----------
record(6, 12, 30, 'npi', 'PROCEDURE NOTE', '04/21/2026', 'S. Banerjee, MD', [
 ('Pre-procedure diagnosis', [('Lumbar disc displacement with radiculopathy, L4-L5 (M51.16).', None)]),
 ('Procedure', [('Left L4-L5 transforaminal epidural steroid injection under fluoroscopic guidance.', 'ex6p12'),
     ('Triamcinolone 80 mg with 2 mL 0.25% bupivacaine. Contrast confirmed epidural spread without vascular uptake.', None)]),
 ('Post-procedure', [('Tolerated well without complication. Pain 6/10 before, 3/10 after.', None),
     ('Two-week follow-up 05/05/2026: approximately 50% relief of radicular pain.', 'ex6p12r')]),
], 'S. Banerjee, MD · 04/21/2026')
record(6, 27, 30, 'npi', 'PROCEDURE NOTE', '07/09/2026', 'S. Banerjee, MD', [
 ('Procedure', [('Repeat left L4-L5 transforaminal epidural steroid injection under fluoroscopic guidance.', 'ex6p27'),
     ('Triamcinolone 80 mg with 2 mL 0.25% bupivacaine.', None)]),
 ('Post-procedure', [('Tolerated well without complication. Discharged ambulatory. Follow-up note on p. 29.', None)]),
], 'S. Banerjee, MD · 07/09/2026')

# ---------- Ex. 7 Pharmacy ----------
FAC['rcp']=('Riverside Community Pharmacy','3880 Main St, Riverside, CA 92501 · (951) 555-0109','RCP-604417','LS')
record(7, 1, 2, 'rcp', 'DISPENSING HISTORY', '03/14/2026 - 10/01/2026', 'Pharmacist on duty', [
 ('Muscle relaxant', [('Cyclobenzaprine 5 mg, #30, 1 tab three times daily as needed. Prescriber K. Moreno, MD. Filled 03/14/2026 and 04/10/2026. No further refills.', 'ex7p1c')]),
 ('Anti-inflammatory', [('Ibuprofen 600 mg, #90, 1 tab every 8 hours with food. Prescriber K. Moreno, MD, then J. Rhee, MD. Filled 03/14, 04/15 and 05/20/2026.', 'ex7p1i')]),
 ('Nerve pain', [('Gabapentin 300 mg, #90, 1 cap three times daily. Prescriber J. Rhee, MD. First filled 04/15/2026; refilled monthly through 09/15/2026.', 'ex7p1g')]),
], 'Printed 10/01/2026 at patient request')

# ---------- Ex. 8 Prior records ----------
record(8, 4, 6, 'vcu', 'URGENT CARE VISIT', '11/18/2019', 'P. Nakamura, PA-C', [
 ('Chief complaint', [('Low back pain after lifting boxes at work two days ago.', None)]),
 ('Assessment', [('Lumbar strain (S39.012A). No radiating symptoms. No imaging indicated.', 'ex8p4')]),
 ('Plan', [('Ibuprofen and activity modification. Return in two weeks if not improved.', None)]),
 ('Follow-up', [('12/02/2019: symptoms resolved; released to full duty. No further visits.', 'ex8p4')]),
], 'P. Nakamura, PA-C · 11/18/2019')

# ---------- Ex. 9 Policy limits ----------
letterpage(9, 1, 'Westbridge Indemnity Company', 'Commercial Auto Claims · P.O. Box 7740, Sacramento, CA 95826 · (916) 555-0193', 'Policy limits letter',
 'July 22, 2026', ['Daniel Reyes, Esq.', 'Reyes & Lin LLP', '3600 Lime St, Suite 410', 'Riverside, CA 92501'],
 ['Re: Insured: Sunline Freight, LLC · Claimant: Maria Alvarez', 'Claim No. WB-26-0418832 · Date of loss: 03/14/2026'],
 [('In response to your request, this letter confirms the coverage available for the above claim.', None),
  ('The commercial auto policy issued to Sunline Freight, LLC and in effect on the date of loss carries bodily injury liability limits of $1,000,000 per occurrence.', 'ex9p1'),
  ('This letter does not waive any rights or defenses under the policy.', None)],
 ('R. Okafor', 'Senior Claims Adjuster'))

# ---------- Ex. 10 Itemized statements ----------
bill(10, 1, 5, 'avmc', 'ex10p1', 'AVM-0418832-01', [
 ('03/14/26','0450','Emergency room facility charge',1,3895.00),('03/14/26','99284','ED visit, high severity',1,3450.00),
 ('03/14/26','72125','CT cervical spine without contrast',1,6980.00),('03/14/26','96372','Injection, intramuscular',1,410.00),
 ('03/14/26','J1885','Ketorolac 15 mg',1,85.00)], 4210.00, 3100.00, '04/28/26', None)
bill(10, 2, 5, 'cri', 'ex10p2', 'CRI-770214-02', [
 ('04/02/26','72148-TC','MRI lumbar spine without contrast, technical',1,4950.00),('04/02/26','72148-26','MRI lumbar spine, professional interpretation',1,1500.00)],
 1180.00, 900.00, '05/20/26', None)
bill(10, 3, 5, 'sso', 'ex10p3', 'SSO-22917-L', [
 ('03/18/26','99204','New patient visit, high complexity',1,950.00),('03/18/26','72110','X-ray lumbar spine, 4 views',1,380.00),
 ('03/18/26','L0637','Lumbar-sacral orthosis',1,1480.00),('04/15/26','99214','Established patient visit',1,425.00),
 ('04/29/26','95910','Nerve conduction studies, 7-8',1,2300.00),('04/29/26','95886','Needle EMG, each extremity',1,2025.00),
 ('06/12/26','99214','Established patient visit',1,425.00),('07/24/26','99214','Established patient visit',1,425.00),
 ('08/20/26','99215','Surgical consultation, high complexity',1,640.00)], 0, 0, '', 'Treatment provided on a medical lien dated 03/18/2026. No payments received. Balance is due from any recovery.')
bill(10, 4, 5, 'hpt', 'ex10p4', 'HPT-5531-07', [
 ('03/24/26','97163','PT evaluation, high complexity',1,440.00),
 ('03/26-09/30','97110/40/530','Therapeutic exercise, manual therapy, activities',35,15400.00)], 6120.00, 2400.00, '10/01/26', None)
bill(10, 5, 5, 'npi', 'ex10p5', 'NPI-10388-11', [
 ('04/21/26','64483','Transforaminal epidural injection, lumbar',1,2800.00),('04/21/26','99152','Moderate sedation',1,480.00),
 ('04/21/26','J3301','Triamcinolone 10 mg',8,120.00),('04/21/26','0490','Ambulatory surgery facility',1,7900.00),
 ('07/09/26','64483','Transforaminal epidural injection, lumbar',1,2800.00),('07/09/26','99152','Moderate sedation',1,480.00),
 ('07/09/26','J3301','Triamcinolone 10 mg',8,120.00),('07/09/26','0490','Ambulatory surgery facility',1,7900.00)], 8900.00, 4300.00, '08/14/26', None)

# ---------- Ex. 11 Wages ----------
letterpage(11, 1, 'Brightline Family Dental', '2250 Market St, Riverside, CA 92501 · (951) 555-0135', 'Wage verification',
 'September 3, 2026', ['Reyes & Lin LLP', '3600 Lime St, Suite 410', 'Riverside, CA 92501'], ['Re: Employment and wage verification · Maria Alvarez'],
 [('Maria Alvarez has worked for our practice as office manager since 2019, on a regular schedule of 40 hours per week.', None),
  ('Her regular weekly wage is $912.50.', 'ex11p1'),
  ('Ms. Alvarez does not work weekends. She was not working on Saturday, March 14, 2026.', 'ex11p1n'),
  ('She was unable to work from March 16, 2026 through July 5, 2026, a period of 16 weeks. We could not accommodate the lifting restrictions in her modified-duty note.', 'ex11p1')],
 ('Dana Whitford', 'Practice Administrator'))

# ---------- Ex. 12 Lien notices ----------
letterpage(12, 1, 'Pacific Crest Health Plan', 'Recovery Unit · P.O. Box 22180, Oakland, CA 94623 · (510) 555-0172', 'Health plan reimbursement claim',
 'August 3, 2026', ['Reyes & Lin LLP', '3600 Lime St, Suite 410', 'Riverside, CA 92501'],
 ['Re: Member: Maria Alvarez · Group: Brightline Family Dental', 'Recovery file PC-26-88104 · Date of loss: 03/14/2026'],
 [('Pacific Crest Health Plan has paid claims for treatment related to the above loss and asserts a right of reimbursement from any third-party recovery.', None),
  ('Claims paid to date: $20,410.00, itemized on the enclosed payment register.', 'ex12p1'),
  ('This group plan is fully insured by Pacific Crest Health Plan. It is not a self-funded employee benefit plan.', 'ex12p1f'),
  ('Please notify us before any settlement is disbursed.', None)],
 ('M. Castellano', 'Recovery Specialist'))
letterpage(12, 2, 'Arlington Valley Medical Center', 'Patient Financial Services · 2100 Arlington Valley Rd, Riverside, CA 92505', 'Notice of hospital lien',
 'April 30, 2026', ['Reyes & Lin LLP', '3600 Lime St, Suite 410', 'Riverside, CA 92501'],
 ['Re: Patient: Maria Alvarez · Account AVM-0418832-01', 'Notice of lien under Civil Code section 3045.1'],
 [('Arlington Valley Medical Center provided emergency services to the above patient on 03/14/2026 and claims a lien on any recovery.', None),
  ('Amount of lien claimed: $7,510.00, the balance after health plan payment and contractual adjustment.', 'ex12p2'),
  ('The account was billed to Pacific Crest Health Plan, which paid $4,210.00 under its contract with this hospital on 04/28/2026.', 'ex12p2c')],
 ('J. Whitcomb', 'Lien Coordinator'))
letterpage(12, 3, 'Cascade Mutual Insurance', 'Personal Auto Claims · P.O. Box 9120, Fresno, CA 93790', 'Medical payments reimbursement',
 'May 12, 2026', ['Reyes & Lin LLP', '3600 Lime St, Suite 410', 'Riverside, CA 92501'],
 ['Re: Insured: Maria Alvarez · Policy CM-4471902', 'Medical payments claim MP-26-30117'],
 [('We have paid $5,000.00 under the medical payments coverage of your client\'s auto policy, the full limit of that coverage.', 'ex12p3'),
  ('Under the reimbursement provision of the policy, we request repayment from any recovery from the responsible party.', None)],
 ('L. Brandt', 'Medical Payments Adjuster'))

# ---------- Ex. 13 Preservation letter ----------
letterpage(13, 1, 'Reyes & Lin LLP', '3600 Lime St, Suite 410, Riverside, CA 92501 · (951) 555-0150', 'Evidence preservation letter',
 'March 20, 2026', ['Risk Management', 'Sunline Freight, LLC', '1800 Commerce Way', 'Ontario, CA 91761'],
 ['Re: Collision of 03/14/2026 on I-215 N · Driver R. Haines · Unit 4417', 'Demand to preserve evidence'],
 [('We represent Maria Alvarez. Please preserve all evidence relating to this collision.', None),
  ('This includes electronic logging device data, engine control module and event data, forward and cab camera video, dispatch tablet messages and usage logs, and the driver qualification and hours-of-service files.', 'ex13p1'),
  ('Do not repair, sell or alter Unit 4417 or its trailer until it has been inspected.', None)],
 ('Daniel Reyes', 'Attorney for Maria Alvarez'))

c.save()
json.dump({'w': W, 'h': H, 'keys': KEYS, 'meta': META, 'bills': BILLS}, open(OUT_JSON, 'w'))
print(len(META), 'pages;', len(KEYS), 'keys')
for k, b in BILLS.items(): print(k, b['total'], b['balance'])
