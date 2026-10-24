"""Build the CaseEdge workspace prototype.

Writes dist/casework.html (the page body published as the claude.ai artifact) and
dist/CaseEdge-Workspace.html (a standalone file that opens directly in a browser).
Run from this folder:  python3 build.py
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
p = lambda *a: os.path.join(HERE, *a)

# Sentence-case the document names that come from the case file index.
DOCS = {'Ed Physician Note': 'Emergency physician note', 'Ed Disposition Summary': 'Emergency department discharge summary',
        'Mri Lumbar Spine Without Contrast': 'MRI report, lumbar and cervical spine', 'Orthopedic Consultation': 'Orthopedic consultation',
        'Orthopedic Follow-Up': 'Orthopedic follow-up note', 'Surgical Consultation': 'Surgical consultation',
        'Physical Therapy Initial Evaluation': 'Physical therapy initial evaluation',
        'Physical Therapy Progress Note · Visit 18': 'Physical therapy progress note, visit 18',
        'Physical Therapy Discharge Summary': 'Physical therapy discharge summary', 'Procedure Note': 'Procedure note',
        'Urgent Care Visit': 'Urgent care visit note',
        'Dispensing History': 'Pharmacy dispensing history', 'Attendance Log': 'Therapy attendance log'}

t = open(p('src', 'template.html')).read()
idx = json.load(open(p('src', 'index2.json')))
for m in idx['meta']:
    m['doc'] = DOCS.get(m['doc'], m['doc'])
b64 = base64.b64encode(open(p('assets', 'casefile.pdf'), 'rb').read()).decode()
assert t.count('/*__DATA__*/') == 1
t = t.replace('/*__DATA__*/', 'const PDF=' + json.dumps(idx, separators=(',', ':')) + ';\nconst PDF_B64="' + b64 + '";')

os.makedirs(p('dist'), exist_ok=True)
# Two layouts from one template: A is left-aligned in the sheet, B centres a modest 1,320px column.
for suffix, js in (('', ''), ('-b', 'document.documentElement.classList.add("v-center");')):
    v = t.replace('/*__VARIANT__*/', js)
    open(p('dist', f'casework{suffix}.html'), 'w').write(v)
    open(p('dist', f'CaseEdge-Workspace{suffix}.html'), 'w').write(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>html,body{margin:0}</style>\n' + v + '\n</html>\n')
print('built', len(t), 'bytes')
