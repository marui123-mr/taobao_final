import os
import json
# 这里引入了 Response，用于强制浏览器渲染网页
from flask import Flask, render_template_string, jsonify, Response

app = Flask(__name__)

# HTML 内嵌在 Python 里，不需要 templates 文件夹
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>淘宝用户行为数据全景分析大屏</title>
    <!-- 保持你论文里的 ECharts 原配置不变 -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background-color: #040f1d; color: #fff; font-family: 'Microsoft YaHei', sans-serif; overflow: hidden; height: 100vh; display: flex; flex-direction: column;}
        .header { height: 60px; text-align: center; font-size: 28px; font-weight: bold; line-height: 60px; color: #00ffff; letter-spacing: 4px; text-shadow: 0 0 15px rgba(0, 255, 255, 0.8); border-bottom: 2px solid #0a2c4e;}
        .main-container { flex: 1; display: flex; padding: 10px 20px; gap: 20px; height: calc(100vh - 60px); }
        .column-side { width: 28%; display: flex; flex-direction: column; gap: 15px; }
        .column-center { width: 44%; display: flex; flex-direction: column; gap: 15px; }
        .box { background: rgba(10, 44, 78, 0.4); border: 1px solid #1a3c5c; border-radius: 8px; padding: 10px; position: relative; box-shadow: 0 0 10px rgba(0, 255, 255, 0.1) inset;}
        .box::before, .box::after { content: ""; position: absolute; width: 15px; height: 15px; border: 2px solid #00ffff; }
        .box::before { top: 0; left: 0; border-right: none; border-bottom: none; border-top-left-radius: 8px;}
        .box::after { bottom: 0; right: 0; border-left: none; border-top: none; border-bottom-right-radius: 8px;}
        .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; height: 15%; }
        .kpi-card { background: rgba(0, 255, 255, 0.05); border: 1px solid #00ffff; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 0 10px rgba(0, 255, 255, 0.2) inset;}
        .kpi-card h3 { font-size: 14px; color: #a0cfff; font-weight: normal; margin-bottom: 5px;}
        .kpi-card p { font-size: 24px; font-weight: bold; color: #ff9900; text-shadow: 0 0 10px rgba(255, 153, 0, 0.5);}
        .chart-box-side { height: 50%; width: 100%; }
        .chart-box-center-top { height: 60%; width: 100%; }
        .chart-box-center-bottom { height: 25%; width: 100%; }
    </style>
</head>
<body>
    <div class="header">淘宝用户行为数据全景分析平台</div>
    <div class="main-container">
        <div class="column-side">
            <div class="box chart-box-side" id="chart-scatter"></div>
            <div class="box chart-box-side" id="chart-hourly"></div>
        </div>
        <div class="column-center">
            <div class="kpi-grid" id="kpi-cards"></div>
            <div class="box chart-box-center-top" id="chart-funnel"></div>
            <div class="box chart-box-center-bottom" id="chart-daily"></div>
        </div>
        <div class="column-side">
            <div class="box chart-box-side" id="chart-category"></div>
            <div class="box chart-box-side" id="chart-rfm"></div>
        </div>
    </div>
    <script>
        const axisLabelColor = '#a0cfff';
        const axisLineColor = '#1a3c5c';
        const splitLineColor = 'rgba(255,255,255,0.05)';
        const titleStyle = { textStyle: { color: '#00ffff', fontSize: 16 }, left: 'center', top: 10 };

        var scatterChart = echarts.init(document.getElementById('chart-scatter'));
        var hourlyChart = echarts.init(document.getElementById('chart-hourly'));
        var funnelChart = echarts.init(document.getElementById('chart-funnel'));
        var dailyChart = echarts.init(document.getElementById('chart-daily'));
        var categoryChart = echarts.init(document.getElementById('chart-category'));
        var rfmChart = echarts.init(document.getElementById('chart-rfm'));

        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                document.getElementById('kpi-cards').innerHTML = `
                    <div class="kpi-card"><h3>总活跃用户数</h3><p>${data.kpi.total_users}</p></div>
                    <div class="kpi-card"><h3>总行为次数</h3><p>${data.kpi.total_behaviors}</p></div>
                    <div class="kpi-card"><h3>购买用户数</h3><p>${data.kpi.buy_users}</p></div>
                    <div class="kpi-card"><h3>全站购买转化率</h3><p>${data.kpi.buy_rate}%</p></div>
                `;

                const scatterData = [];
                data.rfm_clusters.forEach(c => {
                    let count = c.count > 500 ? 150 : (c.count > 50 ? 60 : 20);
                    for(let i=0; i<count; i++) {
                        let r = c.avg_r + (Math.random() - 0.5) * 2;
                        let f = c.avg_f + (Math.random() - 0.5) * c.avg_f * 0.5;
                        if(r < 0) r = 0; if(f < 1) f = 1;
                        scatterData.push({ name: c.label, value: [r.toFixed(1), f.toFixed(1)] });
                    }
                });

                scatterChart.setOption({
                    title: { text: 'RFM 用户聚类散点图', ...titleStyle },
                    tooltip: { formatter: function (param) { return param.data.name + '<br/>R: ' + param.value[0] + '天<br/>F: ' + param.value[1] + '次'; } },
                    legend: { bottom: 5, textStyle: { color: '#fff' }, itemWidth: 10, itemHeight: 10 },
                    grid: { left: '15%', right: '10%', bottom: '15%', top: '20%' },
                    xAxis: { name: 'R (天)', nameTextStyle: {color: axisLabelColor}, type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { show: false } },
                    yAxis: { name: 'F (次)', nameTextStyle: {color: axisLabelColor}, type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { lineStyle: { color: splitLineColor } } },
                    series: ['高价值用户', '发展用户', '保持用户', '流失用户'].map((label, idx) => ({
                        name: label, type: 'scatter', symbolSize: 6, data: scatterData.filter(d => d.name === label),
                        itemStyle: { opacity: 0.7, color: idx === 0 ? '#ff3333' : idx === 1 ? '#ff9900' : idx === 2 ? '#00ffff' : '#666666' }
                    }))
                });

                hourlyChart.setOption({
                    title: { text: '24小时用户活跃分布', ...titleStyle },
                    tooltip: { trigger: 'axis' },
                    grid: { left: '15%', right: '10%', bottom: '15%', top: '20%' },
                    xAxis: { type: 'category', data: data.hourly_pattern.map(h => h.hour + '时'), axisLabel: { color: axisLabelColor, interval: 3 }, axisLine: { lineStyle: { color: axisLineColor } } },
                    yAxis: { type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { lineStyle: { color: splitLineColor } }, axisLine: { lineStyle: { color: axisLineColor } } },
                    series: [{ type: 'line', data: data.hourly_pattern.map(h => h.count), smooth: true, lineStyle: { color: '#00ffff', width: 2 }, itemStyle: { color: '#00ffff' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 255, 255, 0.5)' }, { offset: 1, color: 'rgba(0, 255, 255, 0.01)' }]) } }]
                });

                funnelChart.setOption({
                    title: { text: '用户转化漏斗', ...titleStyle },
                    tooltip: { trigger: 'item', formatter: "{a} <br/>{b} : {c}" },
                    series: [{ name: '转化', type: 'funnel', left: '15%', top: 50, width: '70%', height: '80%', minSize: '25%', maxSize: '100%', sort: 'none', gap: 2, data: data.funnel.map(item => ({ name: item.stage, value: item.users })), label: { position: 'inside', formatter: '{b}: {c}', color: '#fff', fontSize: 14 }, itemStyle: { borderColor: '#040f1d', borderWidth: 1 } }]
                });

                const validTrend = data.daily_trend.filter(d => d.dau > 10);
                dailyChart.setOption({
                    title: { text: '日活跃用户趋势', ...titleStyle },
                    tooltip: { trigger: 'axis' },
                    grid: { left: '8%', right: '5%', bottom: '15%', top: '25%' },
                    xAxis: { type: 'category', data: validTrend.map(d => d.date), axisLabel: { color: axisLabelColor }, axisLine: { lineStyle: { color: axisLineColor } } },
                    yAxis: { type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { lineStyle: { color: splitLineColor } }, axisLine: { lineStyle: { color: axisLineColor } } },
                    series: [{ type: 'line', data: validTrend.map(d => d.dau), smooth: true, lineStyle: { color: '#ff9900', width: 2 }, itemStyle: { color: '#ff9900' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(255, 153, 0, 0.5)' }, { offset: 1, color: 'rgba(255, 153, 0, 0.01)' }]) } }]
                });

                categoryChart.setOption({
                    title: { text: '热销品类 TOP10', ...titleStyle },
                    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
                    grid: { left: '25%', right: '15%', bottom: '10%', top: '20%' },
                    xAxis: { type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { lineStyle: { color: splitLineColor } }, axisLine: { show: false } },
                    yAxis: { type: 'category', data: data.category_top10.map(item => item.category_id).reverse(), axisLabel: { color: axisLabelColor }, axisLine: { lineStyle: { color: axisLineColor } } },
                    series: [{ type: 'bar', data: data.category_top10.map(item => item.buy_count).reverse(), itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#00ffff' }, { offset: 1, color: '#0055ff' }]) }, barWidth: '60%' }]
                });

                rfmChart.setOption({
                    title: { text: 'RFM用户群体规模', ...titleStyle },
                    tooltip: { trigger: 'axis' },
                    grid: { left: '15%', right: '10%', bottom: '15%', top: '20%' },
                    xAxis: { type: 'category', data: data.rfm_clusters.map(c => c.label), axisLabel: { color: axisLabelColor, interval: 0, rotate: 15 }, axisLine: { lineStyle: { color: axisLineColor } } },
                    yAxis: { type: 'value', axisLabel: { color: axisLabelColor }, splitLine: { lineStyle: { color: splitLineColor } }, axisLine: { lineStyle: { color: axisLineColor } } },
                    series: [{ type: 'bar', data: data.rfm_clusters.map(c => c.count), itemStyle: { color: '#ff9900' }, barWidth: '40%' }]
                });
            });

        window.addEventListener('resize', () => {
            scatterChart.resize(); hourlyChart.resize(); funnelChart.resize();
            dailyChart.resize(); categoryChart.resize(); rfmChart.resize();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # 强制返回 text/html 格式，告诉浏览器这是网页，直接渲染不要下载
    return Response(render_template_string(HTML_PAGE), mimetype='text/html')

@app.route('/api/data')
def api_data():
    with open('taobao_summary.json', 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)