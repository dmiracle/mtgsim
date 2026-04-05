"""Scan log API endpoints and dashboard."""

import threading

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from mtgsim.scan_log.db import get_image_path
from mtgsim.scan_log.queries import (
    get_batch_detail,
    get_batch_list,
    get_llm_cost_stats,
    get_scan_detail,
    get_scan_list,
    get_summary_stats,
    label_scan,
)

router = APIRouter(prefix="/scan-log", tags=["scan-log"])


@router.get("/stats")
async def stats() -> dict:
    """Summary statistics across all scans."""
    return get_summary_stats()


@router.get("/llm-costs")
async def llm_costs() -> dict:
    """LLM cost and usage statistics."""
    return get_llm_cost_stats()


@router.get("/scans")
async def scans(
    q: str | None = Query(None, description="Search by extracted or matched card name"),
    pipeline: str | None = Query(None),
    matched: bool | None = Query(None),
    correct: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    """Paginated scan history with filters."""
    offset = (page - 1) * limit
    results, total = get_scan_list(q=q, pipeline=pipeline, matched=matched, correct=correct, limit=limit, offset=offset)
    return {
        "data": results,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/scans/{scan_id}")
async def scan_detail(scan_id: int) -> dict:
    """Full detail for a single scan attempt."""
    detail = get_scan_detail(scan_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
    return detail


class LabelRequest(BaseModel):
    correct: bool
    notes: str | None = None


@router.post("/scans/{scan_id}/label")
async def label(scan_id: int, req: LabelRequest) -> dict:
    """Label a scan as correct or incorrect."""
    ok = label_scan(scan_id, req.correct, req.notes)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
    return {"success": True, "scan_id": scan_id, "correct": req.correct}


@router.get("/batches")
async def batches() -> list[dict]:
    """List all batch scan jobs."""
    return get_batch_list()


@router.get("/batches/{batch_id}")
async def batch_detail(batch_id: int) -> dict:
    """Get detail for a batch scan job."""
    detail = get_batch_detail(batch_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    return detail


class BatchRequest(BaseModel):
    source_dir: str
    api_base: str = "http://localhost:8001"
    add_to_collection: bool = True


@router.post("/batches")
async def start_batch(req: BatchRequest) -> dict:
    """Start a batch scan job in the background."""
    from mtgsim.scan_log.batch import run_batch

    def _run():
        run_batch(req.source_dir, api_base=req.api_base, add_to_collection=req.add_to_collection)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return {"status": "started", "source_dir": req.source_dir}


@router.get("/images/{image_hash}")
async def scan_image(image_hash: str) -> FileResponse:
    """Serve a cached scan image by its SHA256 hash."""
    path = get_image_path(image_hash)
    if not path:
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = "image/png" if path.suffix == ".png" else "image/jpeg"
    return FileResponse(path, media_type=media_type)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    """Server-rendered scan tuning dashboard."""
    return DASHBOARD_HTML


DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scan Tuning Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
    --green: #3fb950; --red: #f85149; --yellow: #d29922;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--text); padding: 20px; line-height: 1.5; }
  h1 { font-size: 1.5em; margin-bottom: 4px; }
  h2 { font-size: 1.1em; color: var(--muted); margin: 20px 0 10px; }
  .subtitle { color: var(--muted); font-size: 0.85em; margin-bottom: 20px; }

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 20px; }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
  .stat-value { font-size: 1.8em; font-weight: 600; }
  .stat-label { color: var(--muted); font-size: 0.8em; }

  .filters { display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; align-items: center; }
  .filters select, .filters button { background: var(--surface); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 6px 12px; font-size: 0.85em; cursor: pointer; }
  .filters button:hover { border-color: var(--accent); }

  table { width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 8px; overflow: hidden; }
  th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid var(--border); font-size: 0.85em; }
  th { color: var(--muted); font-weight: 500; background: var(--surface); position: sticky; top: 0; }
  tr:hover { background: #1c2333; cursor: pointer; }
  .match-yes { color: var(--green); } .match-no { color: var(--red); }
  .correct-yes { color: var(--green); } .correct-no { color: var(--red); } .correct-unlabeled { color: var(--muted); }

  .pagination { display: flex; gap: 8px; margin-top: 10px; justify-content: center; }
  .pagination button { background: var(--surface); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; padding: 4px 12px; cursor: pointer; }
  .pagination button:disabled { opacity: 0.4; cursor: default; }
  .pagination button.active { border-color: var(--accent); color: var(--accent); }

  .detail-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    padding: 16px; margin-top: 16px; display: none; }
  .detail-panel.open { display: block; }
  .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .detail-section { margin-bottom: 12px; }
  .detail-section h3 { font-size: 0.9em; color: var(--accent); margin-bottom: 6px; }
  .detail-kv { display: flex; justify-content: space-between; font-size: 0.82em; padding: 2px 0; }
  .detail-kv .k { color: var(--muted); }
  pre { background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
    padding: 10px; font-size: 0.78em; overflow-x: auto; white-space: pre-wrap; max-height: 200px; }

  .label-btns { display: flex; gap: 8px; margin-top: 8px; }
  .label-btns button { padding: 4px 16px; border-radius: 6px; border: 1px solid var(--border);
    font-size: 0.82em; cursor: pointer; }
  .btn-correct { background: #1a3a2a; color: var(--green); border-color: var(--green); }
  .btn-incorrect { background: #3a1a1a; color: var(--red); border-color: var(--red); }
  .btn-correct:hover { background: #224a34; } .btn-incorrect:hover { background: #4a2424; }

  .cost-table { margin-top: 8px; }
  .cost-table td:nth-child(n+3) { text-align: right; font-variant-numeric: tabular-nums; }

  .tab-bar { display: flex; gap: 0; margin-bottom: 16px; border-bottom: 1px solid var(--border); }
  .tab { padding: 8px 16px; cursor: pointer; color: var(--muted); border-bottom: 2px solid transparent; font-size: 0.9em; }
  .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
  .tab-content { display: none; } .tab-content.active { display: block; }
</style>
</head>
<body>

<h1>Scan Tuning Dashboard</h1>
<p class="subtitle">Internal tool for comparing pipelines and tuning OCR parameters</p>

<div id="stats" class="stats-grid"></div>

<div class="tab-bar">
  <div class="tab active" onclick="switchTab('history')">Scan History</div>
  <div class="tab" onclick="switchTab('costs')">LLM Costs</div>
  <div class="tab" onclick="switchTab('batches')">Batch Jobs</div>
</div>

<div id="tab-history" class="tab-content active">
  <div class="filters">
    <input id="f-search" type="text" placeholder="Search card name..." style="background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 12px;font-size:0.85em;width:200px" onkeydown="if(event.key==='Enter')loadScans()">
    <select id="f-pipeline"><option value="">All Pipelines</option>
      <option value="openai">openai</option><option value="tesseract">tesseract</option><option value="mock">mock</option></select>
    <select id="f-matched"><option value="">All Results</option>
      <option value="true">Matched</option><option value="false">Unmatched</option></select>
    <select id="f-correct"><option value="">All Labels</option>
      <option value="true">Correct</option><option value="false">Incorrect</option></select>
    <button onclick="loadScans()">Filter</button>
  </div>
  <table>
    <thead><tr><th>#</th><th>Time</th><th>Pipeline</th><th>Extracted</th><th>Matched</th><th>Card</th><th>Confidence</th><th>Latency</th><th>Label</th></tr></thead>
    <tbody id="scan-rows"></tbody>
  </table>
  <div class="pagination" id="pagination"></div>
  <div class="detail-panel" id="detail-panel"></div>
</div>

<div id="tab-costs" class="tab-content">
  <div id="cost-stats" class="stats-grid"></div>
  <h2>Cost by Model</h2>
  <table class="cost-table">
    <thead><tr><th>Provider</th><th>Model</th><th>Calls</th><th>Prompt Tok</th><th>Completion Tok</th><th>Cost (USD)</th><th>Avg Latency</th></tr></thead>
    <tbody id="cost-rows"></tbody>
  </table>
</div>

<div id="tab-batches" class="tab-content">
  <div id="batch-stats" class="stats-grid"></div>
  <h2>Batch Runs</h2>
  <table>
    <thead><tr><th>#</th><th>Started</th><th>Status</th><th>Images</th><th>OA Matched</th><th>TS Matched</th><th>Agreed</th><th>Added</th><th>Time</th></tr></thead>
    <tbody id="batch-rows"></tbody>
  </table>
  <div class="detail-panel" id="batch-detail-panel"></div>
</div>

<script>
const API = '/api/scan-log';
let currentPage = 1;
let selectedScanId = null;

async function api(path) {
  const r = await fetch(API + path);
  return r.json();
}

async function postApi(path, body) {
  const r = await fetch(API + path, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body) });
  return r.json();
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab-content#tab-${name}`).classList.add('active');
  event.target.classList.add('active');
  if (name === 'costs') loadCosts();
  if (name === 'batches') loadBatches();
}

async function loadStats() {
  const s = await api('/stats');
  document.getElementById('stats').innerHTML = `
    <div class="stat-card"><div class="stat-value">${s.total_scans}</div><div class="stat-label">Total Scans</div></div>
    <div class="stat-card"><div class="stat-value">${s.match_rate ?? '—'}%</div><div class="stat-label">Match Rate</div></div>
    <div class="stat-card"><div class="stat-value">${s.accuracy ?? '—'}%</div><div class="stat-label">Accuracy (labeled)</div></div>
    <div class="stat-card"><div class="stat-value">${s.total_labeled}</div><div class="stat-label">Labeled</div></div>
    ${Object.entries(s.pipelines).map(([p, v]) => `
      <div class="stat-card"><div class="stat-value">${v.total}</div><div class="stat-label">${p} scans</div></div>
    `).join('')}
  `;
}

async function loadScans(page) {
  currentPage = page || 1;
  const p = new URLSearchParams();
  const search = document.getElementById('f-search').value;
  const pipeline = document.getElementById('f-pipeline').value;
  const matched = document.getElementById('f-matched').value;
  const correct = document.getElementById('f-correct').value;
  if (search) p.set('q', search);
  if (pipeline) p.set('pipeline', pipeline);
  if (matched) p.set('matched', matched);
  if (correct) p.set('correct', correct);
  p.set('page', currentPage);
  p.set('limit', 30);

  const data = await api('/scans?' + p.toString());
  const tbody = document.getElementById('scan-rows');
  tbody.innerHTML = data.data.map(s => `
    <tr onclick="loadDetail(${s.id})" class="${selectedScanId === s.id ? 'selected' : ''}">
      <td>${s.id}</td>
      <td>${s.created_at ? new Date(s.created_at).toLocaleString() : '—'}</td>
      <td>${s.pipeline}</td>
      <td>${s.extracted_name}</td>
      <td class="${s.matched ? 'match-yes' : 'match-no'}">${s.matched ? 'Yes' : 'No'}</td>
      <td>${s.matched_card_name || '—'}</td>
      <td>${s.match_confidence != null ? s.match_confidence.toFixed(1) : '—'}</td>
      <td>${s.total_ms != null ? s.total_ms.toFixed(0) + 'ms' : '—'}</td>
      <td class="${s.correct === true ? 'correct-yes' : s.correct === false ? 'correct-no' : 'correct-unlabeled'}">
        ${s.correct === true ? '✓' : s.correct === false ? '✗' : '—'}</td>
    </tr>
  `).join('');

  const pag = document.getElementById('pagination');
  let btns = '';
  if (data.pages > 1) {
    btns += `<button ${currentPage <= 1 ? 'disabled' : ''} onclick="loadScans(${currentPage - 1})">Prev</button>`;
    btns += `<span style="color:var(--muted);padding:4px 8px">${currentPage} / ${data.pages}</span>`;
    btns += `<button ${currentPage >= data.pages ? 'disabled' : ''} onclick="loadScans(${currentPage + 1})">Next</button>`;
  }
  pag.innerHTML = btns;
}

async function loadDetail(id) {
  selectedScanId = id;
  const d = await api(`/scans/${id}`);
  const panel = document.getElementById('detail-panel');
  panel.classList.add('open');

  const timingHtml = d.timing ? `
    <div class="detail-kv"><span class="k">Preprocess</span><span>${d.timing.preprocess_ms.toFixed(1)}ms</span></div>
    <div class="detail-kv"><span class="k">Extract</span><span>${d.timing.extract_ms.toFixed(1)}ms</span></div>
    <div class="detail-kv"><span class="k">Match</span><span>${d.timing.match_ms.toFixed(1)}ms</span></div>
    <div class="detail-kv"><span class="k">Total</span><span>${d.timing.total_ms.toFixed(1)}ms</span></div>
  ` : '<em>No timing data</em>';

  const candidatesHtml = d.candidates.length > 0
    ? `<table style="width:100%"><thead><tr><th>#</th><th>Card</th><th>Score</th><th>Components</th></tr></thead><tbody>
       ${d.candidates.map(c => `<tr><td>${c.rank}</td><td>${c.card_name}</td><td>${c.score.toFixed(1)}</td>
         <td style="font-size:0.75em;color:var(--muted)">${JSON.stringify(c.component_scores)}</td></tr>`).join('')}
       </tbody></table>`
    : '<em>No candidates</em>';

  const llmHtml = d.llm_calls.length > 0
    ? d.llm_calls.map(lc => `
        <div class="detail-kv"><span class="k">${lc.provider}/${lc.model}</span><span>${lc.status}</span></div>
        <div class="detail-kv"><span class="k">Tokens</span><span>${lc.prompt_tokens} + ${lc.completion_tokens} = ${lc.total_tokens}</span></div>
        <div class="detail-kv"><span class="k">Cost</span><span>$${lc.cost_usd.toFixed(4)}</span></div>
        <div class="detail-kv"><span class="k">Latency</span><span>${lc.latency_ms.toFixed(0)}ms</span></div>
      `).join('<hr style="border-color:var(--border);margin:6px 0">')
    : '<em>No LLM calls</em>';

  panel.innerHTML = `
    <div class="detail-grid">
      <div>
        <div class="detail-section">
          <h3>Scan #${d.id}</h3>
          <div class="detail-kv"><span class="k">Pipeline</span><span>${d.pipeline}</span></div>
          <div class="detail-kv"><span class="k">Extracted Name</span><span>${d.extracted_name}</span></div>
          <div class="detail-kv"><span class="k">Matched</span><span class="${d.matched ? 'match-yes' : 'match-no'}">${d.matched ? d.matched_card_name : 'No match'}</span></div>
          <div class="detail-kv"><span class="k">Confidence</span><span>${d.match_confidence != null ? d.match_confidence.toFixed(1) : '—'}</span></div>
          <div class="detail-kv"><span class="k">Match Type</span><span>${d.match_type}</span></div>
          <div class="detail-kv"><span class="k">Image</span><span>${d.image_size_bytes} bytes (${d.mime_type})</span></div>
        </div>
        <div class="detail-section">
          <h3>Scanned Image</h3>
          <img src="${API}/images/${d.image_hash}" alt="Scanned card" style="max-width:250px;border-radius:6px;border:1px solid var(--border);"
               onerror="this.style.display='none'">
        </div>
        <div class="detail-section"><h3>Timing</h3>${timingHtml}</div>
        <div class="detail-section"><h3>LLM Calls</h3>${llmHtml}</div>
        <div class="detail-section">
          <h3>Label</h3>
          <div class="label-btns">
            <button class="btn-correct" onclick="labelScan(${d.id}, true)">Correct ✓</button>
            <button class="btn-incorrect" onclick="labelScan(${d.id}, false)">Incorrect ✗</button>
          </div>
        </div>
      </div>
      <div>
        <div class="detail-section"><h3>Match Candidates</h3>${candidatesHtml}</div>
        <div class="detail-section"><h3>Params</h3><pre>${d.params ? JSON.stringify(d.params, null, 2) : 'None'}</pre></div>
        <div class="detail-section"><h3>Raw OCR Text</h3><pre>${d.raw_text || '(empty)'}</pre></div>
      </div>
    </div>
  `;
}

async function labelScan(id, correct) {
  await postApi(`/scans/${id}/label`, { correct });
  loadScans(currentPage);
  loadDetail(id);
  loadStats();
}

async function loadCosts() {
  const c = await api('/llm-costs');
  document.getElementById('cost-stats').innerHTML = `
    <div class="stat-card"><div class="stat-value">${c.total_calls}</div><div class="stat-label">Total LLM Calls</div></div>
    <div class="stat-card"><div class="stat-value">$${c.total_cost_usd.toFixed(4)}</div><div class="stat-label">Total Cost</div></div>
    <div class="stat-card"><div class="stat-value">${(c.total_tokens / 1000).toFixed(1)}k</div><div class="stat-label">Total Tokens</div></div>
    <div class="stat-card"><div class="stat-value">${c.error_count}</div><div class="stat-label">Errors</div></div>
  `;
  document.getElementById('cost-rows').innerHTML = c.models.map(m => `
    <tr>
      <td>${m.provider}</td><td>${m.model}</td><td>${m.calls}</td>
      <td>${m.prompt_tokens.toLocaleString()}</td><td>${m.completion_tokens.toLocaleString()}</td>
      <td>$${m.total_cost_usd.toFixed(4)}</td><td>${m.avg_latency_ms.toFixed(0)}ms</td>
    </tr>
  `).join('');
}

async function loadBatches() {
  const batches = await api('/batches');
  const tbody = document.getElementById('batch-rows');
  tbody.innerHTML = batches.map(b => `
    <tr onclick="loadBatchDetail(${b.id})" style="cursor:pointer">
      <td>${b.id}</td>
      <td>${b.created_at ? new Date(b.created_at).toLocaleString() : '—'}</td>
      <td style="color:${b.status === 'completed' ? 'var(--green)' : b.status === 'running' ? 'var(--yellow)' : 'var(--red)'}">${b.status}</td>
      <td>${b.processed}/${b.total_images}</td>
      <td>${b.matched_openai}</td>
      <td>${b.matched_tesseract}</td>
      <td>${b.agreed}</td>
      <td>${b.added_to_collection}</td>
      <td>${b.total_time_s ? b.total_time_s.toFixed(1) + 's' : '—'}</td>
    </tr>
  `).join('');

  if (batches.length > 0) {
    const latest = batches[0];
    document.getElementById('batch-stats').innerHTML = `
      <div class="stat-card"><div class="stat-value">${batches.length}</div><div class="stat-label">Total Batches</div></div>
      <div class="stat-card"><div class="stat-value">${latest.processed}</div><div class="stat-label">Latest: Images</div></div>
      <div class="stat-card"><div class="stat-value">${latest.matched_openai}</div><div class="stat-label">Latest: OA Matched</div></div>
      <div class="stat-card"><div class="stat-value">${latest.matched_tesseract}</div><div class="stat-label">Latest: TS Matched</div></div>
      <div class="stat-card"><div class="stat-value">${latest.agreed}</div><div class="stat-label">Latest: Agreed</div></div>
      <div class="stat-card"><div class="stat-value">${latest.added_to_collection}</div><div class="stat-label">Latest: Added</div></div>
    `;
  }
}

async function loadBatchDetail(id) {
  const d = await api(`/batches/${id}`);
  const panel = document.getElementById('batch-detail-panel');
  panel.classList.add('open');

  const imageRows = d.images.map(img => {
    const oa = img.pipelines.openai || {};
    const ts = img.pipelines.tesseract || {};
    const agree = oa.extracted_name && ts.extracted_name && oa.extracted_name === ts.extracted_name;
    return `<tr>
      <td><img src="${API}/images/${img.image_hash}" style="height:40px;border-radius:3px" onerror="this.style.display='none'"></td>
      <td class="${oa.matched ? 'match-yes' : 'match-no'}">${oa.extracted_name || '—'}</td>
      <td>${oa.matched ? oa.matched_card_name || '?' : '—'}</td>
      <td class="${ts.matched ? 'match-yes' : 'match-no'}">${ts.extracted_name || '—'}</td>
      <td>${ts.matched ? ts.matched_card_name || '?' : '—'}</td>
      <td style="color:${agree ? 'var(--green)' : 'var(--red)'}">${agree ? '✓' : '✗'}</td>
      <td>${oa.added_to_collection ? '✓' : ''}</td>
    </tr>`;
  }).join('');

  panel.innerHTML = `
    <h3>Batch #${d.id} — ${d.status}</h3>
    <div class="stats-grid" style="margin:12px 0">
      <div class="stat-card"><div class="stat-value">${d.processed}/${d.total_images}</div><div class="stat-label">Processed</div></div>
      <div class="stat-card"><div class="stat-value">${d.total_images > 0 ? (d.matched_openai / d.total_images * 100).toFixed(0) : 0}%</div><div class="stat-label">OA Match Rate</div></div>
      <div class="stat-card"><div class="stat-value">${d.total_images > 0 ? (d.matched_tesseract / d.total_images * 100).toFixed(0) : 0}%</div><div class="stat-label">TS Match Rate</div></div>
      <div class="stat-card"><div class="stat-value">${d.total_images > 0 ? (d.agreed / d.total_images * 100).toFixed(0) : 0}%</div><div class="stat-label">Agreement</div></div>
      <div class="stat-card"><div class="stat-value">${d.total_time_s ? d.total_time_s.toFixed(1) + 's' : '—'}</div><div class="stat-label">Total Time</div></div>
      <div class="stat-card"><div class="stat-value">${d.added_to_collection}</div><div class="stat-label">Added to Collection</div></div>
    </div>
    <table>
      <thead><tr><th>Image</th><th>OA Extracted</th><th>OA Match</th><th>TS Extracted</th><th>TS Match</th><th>Agree</th><th>Added</th></tr></thead>
      <tbody>${imageRows}</tbody>
    </table>
  `;
}

// Init
loadStats();
loadScans();
</script>
</body>
</html>
"""
