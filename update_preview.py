import sys

with open('dashboard/preview_renderer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
in_string = False
for i, line in enumerate(lines):
    if i == 213:
        out.append('    def _build_html(self, chart_images: dict) -> dict:\n')
        continue
    if i == 222:
        out.append('        return {\n')
        out.append('            "title": self.title,\n')
        out.append('            "kpi_cards_html": kpi_cards_html,\n')
        out.append('            "charts_p1_html": charts_p1_html,\n')
        out.append('            "charts_p2_html": charts_p2_html,\n')
        out.append('            "charts_p3_html": charts_p3_html,\n')
        out.append('            "charts_p4_html": charts_p4_html,\n')
        out.append('            "insights_html": insights_html,\n')
        out.append('            "quality_html": quality_html,\n')
        out.append('        }\n')
        in_string = True
        continue
    if in_string:
        if i >= 513: # Just before _kpi_cards_html starts
            in_string = False
        continue
    
    out.append(line)

with open('dashboard/preview_renderer.py', 'w', encoding='utf-8') as f:
    f.writelines(out)

print("Done")
