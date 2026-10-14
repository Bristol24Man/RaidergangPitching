CSS = '''
<style>
  @page { size: letter; margin: 0.35in; }
  * { box-sizing: border-box; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important; }
  }
  body { font-family: 'Roboto Mono', 'Courier New', monospace; margin:0; padding:0; color:#1a1a1a; font-size:11px; }
  .page { width: 7.8in; margin: 0 auto; padding: 10px 6px; page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  .header { display:flex; align-items:center; border-bottom:3px solid #d3a24c; padding-bottom:8px; margin-bottom:10px; }
  .logo { height:70px; width:auto; flex:0 0 auto; display:block; }
  .header-title { flex:1 1 auto; min-width:0; padding-left:14px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .pitcher-name { font-size:20px; font-weight:bold; color:#0a0a0a; }
  .report-sub { font-size:16px; color:#1b6b3a; font-weight:bold; }
  .header-date { flex:0 0 auto; font-size:13px; font-weight:bold; color:#444; white-space:nowrap; padding-left:10px; }

  table { width:100%; border-collapse:collapse; margin-bottom:8px; }
  .metric-table th { background:#0a0a0a; color:#d3a24c; padding:10px 5px; font-size:15px; border:1px solid #bbb; }
  .metric-table td { border:1px solid #ddd; padding:9px 5px; text-align:center; font-size:14.5px; }
  .pitch-cell { text-align:left !important; padding-left:10px !important; font-weight:bold; position:relative; font-size:15px; }
  .tag { font-size:10px; color:#888; font-weight:normal; margin-left:6px; }
  .tag-season { font-size:12.5px; font-style:italic; color:#999; }
  .season-row td { color:#999; font-style:italic; background:#fafafa; font-size:12.5px; }
  .season-note { text-align:left !important; padding-left:10px !important; }

  .legend-row { text-align:center; margin: 10px 0 16px 0; font-size:15px; }
  .leg-item { margin: 0 14px; display:inline-flex; align-items:center; }
  .leg-dot { width:14px; height:14px; border-radius:50%; display:inline-block; margin-right:6px; border:1px solid #0002; }

  .charts-row { display:flex; justify-content:space-between; gap:14px; align-items:flex-start; margin-top:8px; }
  .chart-box { flex:1 1 0; min-width:0; text-align:center; }
  .chart-title { font-weight:bold; font-size:15px; margin-bottom:4px; color:#0a0a0a; }
  .chart-box svg { width:100%; height:auto; max-width:100%; display:block; }
  .page1-note { text-align:center; font-style:italic; color:#777; font-size:11px; margin-top:14px; }

  .stat-table th { background:#0a0a0a; color:#d3a24c; padding:7px 3px; font-size:11.5px; border:1px solid #bbb; }
  .stat-table td { border:1px solid #ddd; padding:6px 3px; text-align:center; font-size:12px; }
  .goal-row td { font-style:italic; color:#555; background:#f7f4ee; font-size:11px; }

  .section-bar { background:#0a0a0a; color:#fff; text-align:center; font-weight:bold; padding:6px; font-size:13px; letter-spacing:1px; margin-top:12px; }
  .section-sub { text-align:center; font-size:10.5px; color:#666; margin:3px 0 8px 0; font-style:italic; }
  .zone-row { display:flex; align-items:flex-start; gap:10px; margin-bottom:6px; }
  .zone-col { text-align:center; flex:0 0 auto; }
  .zone-label { font-weight:bold; font-size:12px; margin-bottom:3px; }
  .zone-info { flex:1; padding-top:10px; font-size:11px; }
  .legend-col { display:flex; flex-direction:column; gap:4px; margin-bottom:10px; }
  .legend-col .leg-item { margin:0; justify-content:flex-start; }
  .info-line { margin-bottom:6px; line-height:1.4; }
</style>
'''
