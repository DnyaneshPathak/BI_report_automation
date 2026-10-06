import os
import re

file_path = 'src/bi_automation/web/templates/preview.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''                let option = {
                    dataset: { source: source },
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'category' },
                    yAxis: { type: 'value' },
                    series: series,
                    grid: (data.layout && data.layout.grid) ? data.layout.grid : { containLabel: true }
                };
                
                if (data.layout && data.layout.xAxis_rotate !== undefined && seriesType !== "pie" && seriesType !== "donut") {
                    option.xAxis.axisLabel = { rotate: data.layout.xAxis_rotate };
                }
'''

content = re.sub(r'                let option = {.*?                    series: series\n                };', replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated preview.html to use layout meta")
