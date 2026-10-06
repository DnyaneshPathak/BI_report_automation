import os
import re

file_path = 'src/bi_automation/web/templates/preview.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We will replace everything from <script> to </script> at the bottom.
js_replacement = '''<script>
document.addEventListener("DOMContentLoaded", () => {
    const computedFigures = {{ computed_figures_json|safe }};
    const plan = {{ plan_json|safe }};
    const root = document.getElementById("dashboard-root");
    
    if (!plan.items || plan.items.length === 0) {
        root.innerHTML = "<div style='padding: 2rem; background: #fee2e2; color: #991b1b; border-radius: 8px;'>No dashboard items generated. Please try a more specific prompt.</div>";
        return;
    }
    
    const kpis = plan.items.filter(i => i.type === "kpi");
    const visuals = plan.items.filter(i => i.type === "visual" || i.type === "table");
    
    if (kpis.length > 0) {
        let kpiHtml = "<div class='kpi-container'>";
        kpis.forEach(kpi => {
            const data = computedFigures[kpi.id];
            if (data && !data.error) {
                kpiHtml += 
                    <div class='kpi-card'>
                        <div class='kpi-title'></div>
                        <div class='kpi-value'></div>
                    </div>
                ;
            } else {
                kpiHtml += 
                    <div class='kpi-card' style='border-top-color: #ef4444;'>
                        <div class='kpi-title'></div>
                        <div class='kpi-value' style='color: #ef4444; font-size: 1rem;'>?? </div>
                    </div>
                ;
            }
        });
        kpiHtml += "</div>";
        root.insertAdjacentHTML('beforeend', kpiHtml);
    }
    
    if (visuals.length > 0) {
        let visualHtml = "<div class='visual-container'>";
        visuals.forEach(vis => {
            visualHtml += 
                <div class='visual-card' id='card-'>
                    <div class='visual-header'>
                        <h3 class='visual-title'></h3>
                        <div class='chart-controls'>
                            <button class='chart-btn' onclick='toggleSort("")'>?? Sort</button>
                            <select class='chart-select' onchange='changeType("", this.value)'>
                                <option value='bar' >Bar</option>
                                <option value='line' >Line</option>
                                <option value='pie' >Pie</option>
                                <option value='table' >Table</option>
                            </select>
                        </div>
                    </div>
                    <div id='chart-' class='chart-box'></div>
                </div>
            ;
        });
        visualHtml += "</div>";
        root.insertAdjacentHTML('beforeend', visualHtml);
        
        window.dashboardCharts = {};
        window.dashboardStates = {};
        
        visuals.forEach(vis => {
            const data = computedFigures[vis.id];
            const container = document.getElementById(chart-);
            
            if (!data || data.error) {
                container.innerHTML = <div style='color: #ef4444; padding: 20px;'>?? </div>;
                return;
            }
            
            window.dashboardStates[vis.id] = {
                source: data.dataset.source,
                type: data.chart_type === "table" || vis.type === "table" ? "table" : (data.chart_type === "column" ? "bar" : data.chart_type),
                sortDir: 'none',
                layout: data.layout
            };
            
            renderVisual(vis.id, container);
        });
    }
});

function renderVisual(id, container) {
    const state = window.dashboardStates[id];
    let source = [...state.source];
    
    // Apply sorting (skipping header row)
    if (state.sortDir !== 'none' && source.length > 2) {
        const header = source[0];
        let dataRows = source.slice(1);
        dataRows.sort((a, b) => {
            let valA = a[1]; let valB = b[1];
            if (valA === valB) return 0;
            if (state.sortDir === 'asc') return valA > valB ? 1 : -1;
            return valA < valB ? 1 : -1;
        });
        source = [header, ...dataRows];
    }
    
    if (state.type === 'table') {
        if (window.dashboardCharts[id]) {
            window.dashboardCharts[id].dispose();
            delete window.dashboardCharts[id];
        }
        let tHtml = "<div class='table-container'><table><thead><tr>";
        source[0].forEach(h => tHtml += <th></th>);
        tHtml += "</tr></thead><tbody>";
        for (let i = 1; i < source.length; i++) {
            tHtml += "<tr>";
            source[i].forEach(c => {
                let val = typeof c === 'number' ? (c % 1 === 0 ? c : c.toFixed(2)) : c;
                tHtml += <td></td>;
            });
            tHtml += "</tr>";
        }
        tHtml += "</tbody></table></div>";
        container.innerHTML = tHtml;
        container.style.height = "auto";
        container.style.maxHeight = "350px";
        container.style.overflowY = "auto";
    } else {
        container.innerHTML = "";
        let chart = window.dashboardCharts[id];
        if (!chart) {
            chart = echarts.init(container);
            window.dashboardCharts[id] = chart;
            window.addEventListener('resize', () => chart.resize());
        }
        
        const seriesCount = source[0].length - 1;
        let series = Array.from({length: seriesCount}, () => ({ type: state.type }));
        
        let option = {
            dataset: { source: source },
            tooltip: { trigger: 'axis' },
            xAxis: { type: 'category' },
            yAxis: { type: 'value' },
            series: series,
            grid: (state.layout && state.layout.grid) ? state.layout.grid : { containLabel: true }
        };
        
        if (state.type === "pie" || state.type === "donut") {
            option.xAxis = undefined;
            option.yAxis = undefined;
            option.tooltip = { trigger: 'item' };
            option.series = [{
                type: 'pie',
                radius: state.type === "donut" ? ['40%', '70%'] : '50%',
                encode: { itemName: source[0][0], value: source[0][1] }
            }];
        } else if (state.layout && state.layout.xAxis_rotate !== undefined) {
            option.xAxis.axisLabel = { rotate: state.layout.xAxis_rotate };
        }
        
        // Disable animation when motion reduction is requested (Dynamic !== Live requirement)
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) {
            option.animation = false;
        }
        
        chart.setOption(option, true);
    }
}

window.toggleSort = function(id) {
    const state = window.dashboardStates[id];
    if (state.sortDir === 'none') state.sortDir = 'desc';
    else if (state.sortDir === 'desc') state.sortDir = 'asc';
    else state.sortDir = 'none';
    renderVisual(id, document.getElementById(chart-));
};

window.changeType = function(id, newType) {
    const state = window.dashboardStates[id];
    state.type = newType;
    renderVisual(id, document.getElementById(chart-));
};
</script>'''

content = re.sub(r'<script>\ndocument\.addEventListener\("DOMContentLoaded".*?</script>', js_replacement, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated JS in preview.html")
