/**
 * RevMatrix AI - Interactive Dashboard & Batch Engine
 * Razorpay Buildathon (Track 03)
 */

let activeCases = [];
let activeAuditLogs = [];
let currentVoiceCaseId = null;

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    lucide.createIcons();
  }
  initTabs();
  initEventListeners();
  loadAllData();
});

// Tab Navigation
function initTabs() {
  const navButtons = document.querySelectorAll('.nav-item');
  const panes = document.querySelectorAll('.tab-pane');
  const pageHeading = document.getElementById('page-heading');
  const pageSub = document.getElementById('page-sub');

  const titles = {
    'tab-overview': { title: 'Executive Command Center', sub: 'Autonomous closed-loop revenue recovery across Indian payment rails' },
    'tab-batch': { title: 'Autonomous Batch Test Bench', sub: 'Process 50+ benchmark cases across all 7 problem directions with granular agent reasoning' },
    'tab-voice': { title: 'Hinglish Conversational Voice & Chat', sub: 'Interactive dialogue simulation, audio synthesis, and Promise-to-Pay (PTP) tracker' },
    'tab-audit': { title: 'Cryptographic Audit Trail', sub: 'Every diagnostic step, tool execution, and stopping rule is SHA-256 block-linked' },
    'tab-webhook': { title: 'Live Webhook Injector', sub: 'Simulate any incoming failure or degradation event and watch RevMatrix AI resolve it' }
  };

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      panes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      const targetPane = document.getElementById(tabId);
      if (targetPane) targetPane.classList.add('active');

      if (titles[tabId]) {
        pageHeading.textContent = titles[tabId].title;
        pageSub.textContent = titles[tabId].sub;
      }
    });
  });
}

function initEventListeners() {
  // Reset Button
  document.getElementById('btn-reset-batch').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/recovery/batch/reset', { method: 'POST' });
      const data = await res.json();
      alert('Dataset reset to 50 fresh benchmark cases.');
      loadAllData();
    } catch (e) {
      console.error(e);
    }
  });

  // Run Batch Recovery Button
  document.getElementById('btn-run-batch-top').addEventListener('click', async () => {
    const btn = document.getElementById('btn-run-batch-top');
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader" class="spin"></i> Processing Batch...`;
    if (window.lucide) lucide.createIcons();

    try {
      const res = await fetch('/api/recovery/batch/run-all', { method: 'POST' });
      const data = await res.json();
      await loadAllData();
      alert(`Autonomous Recovery Completed!\nProcessed: ${data.processed_cases} cases.\nRecovered Revenue: ₹${data.metrics.total_recovered_inr.toLocaleString('en-IN')}`);
    } catch (e) {
      alert('Error running batch: ' + e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="play"></i> <span>Run Autonomous Recovery</span>`;
      if (window.lucide) lucide.createIcons();
    }
  });

  // Filters
  document.getElementById('filter-category').addEventListener('change', renderCasesTable);
  document.getElementById('filter-status').addEventListener('change', renderCasesTable);

  // Modal Close
  document.getElementById('modal-close-btn').addEventListener('click', () => {
    document.getElementById('case-modal').style.display = 'none';
  });

  // Voice Case Selector
  document.getElementById('voice-case-select').addEventListener('change', (e) => {
    loadVoiceScript(e.target.value);
  });

  // Voice Play Audio Button (Browser TTS)
  document.getElementById('btn-play-audio').addEventListener('click', () => {
    const scriptText = document.getElementById('voice-script-text').textContent;
    if (!scriptText || scriptText.includes('Select a case')) return;

    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(scriptText);
      utterance.lang = 'hi-IN';
      utterance.rate = 0.95;
      utterance.pitch = 1.05;
      window.speechSynthesis.speak(utterance);
    } else {
      alert('Browser speech synthesis not supported on this device.');
    }
  });

  // Quick chips for voice
  document.querySelectorAll('.quick-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.getElementById('voice-user-input').value = chip.dataset.text;
      sendVoiceTurn(chip.dataset.text);
    });
  });

  // Send Voice Turn
  document.getElementById('btn-send-voice-turn').addEventListener('click', () => {
    const input = document.getElementById('voice-user-input');
    if (input.value.trim()) {
      sendVoiceTurn(input.value.trim());
      input.value = '';
    }
  });

  // PTP Submit
  document.getElementById('btn-submit-ptp').addEventListener('click', async () => {
    const text = document.getElementById('ptp-input-text').value.trim();
    if (!text) return;

    const caseId = currentVoiceCaseId || (activeCases[0] ? activeCases[0].id : null);
    if (!caseId) return;

    try {
      const res = await fetch('/api/recovery/ptp/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId, user_statement: text })
      });
      const data = await res.json();
      
      const resultBox = document.getElementById('ptp-result-box');
      resultBox.style.display = 'block';
      resultBox.innerHTML = `
        <div class="info-callout">
          <i data-lucide="check-circle-2"></i>
          <div>
            <strong>Promise-to-Pay Active!</strong><br>
            Committed Date: <code>${data.ptp.promised_date.substring(0, 10)}</code><br>
            Account Suspension Paused & Reminder Scheduled.
          </div>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      loadAllData();
    } catch (e) {
      alert('PTP submission error: ' + e);
    }
  });

  // Webhook Injector Form
  document.getElementById('webhook-inject-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('btn-inject-submit');
    btn.disabled = true;

    const payload = {
      event: document.getElementById('wh-event').value,
      amount: parseFloat(document.getElementById('wh-amount').value),
      customer_name: document.getElementById('wh-name').value,
      customer_phone: document.getElementById('wh-phone').value,
      customer_email: `${document.getElementById('wh-name').value.toLowerCase().replace(/\s+/g, '')}@example.com`,
      bank: document.getElementById('wh-bank').value,
      error_code: document.getElementById('wh-error').value
    };

    try {
      const res = await fetch('/api/recovery/webhook/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const resultBox = document.getElementById('webhook-result-card');
      resultBox.style.display = 'block';
      resultBox.innerHTML = `
        <div class="card" style="background: rgba(0, 242, 254, 0.05); border-color: rgba(0, 242, 254, 0.3);">
          <h4>⚡ Webhook Ingested & Resolved Autonomously</h4>
          <p><strong>Case ID:</strong> <code>${data.case.id}</code></p>
          <p><strong>Status:</strong> <span class="badge ${getStatusBadge(data.case.status)}">${data.case.status}</span></p>
          <p><strong>Root Cause:</strong> ${data.case.diagnostic ? data.case.diagnostic.root_cause : 'N/A'}</p>
          <p><strong>Razorpay Action:</strong> ${data.case.active_intervention ? data.case.active_intervention.action_description : 'N/A'}</p>
        </div>
      `;
      loadAllData();
    } catch (err) {
      alert('Webhook error: ' + err);
    } finally {
      btn.disabled = false;
    }
  });
}

async function loadAllData() {
  try {
    const [metricsRes, casesRes, auditRes] = await Promise.all([
      fetch('/api/analytics/metrics'),
      fetch('/api/recovery/cases'),
      fetch('/api/analytics/audit-logs?limit=50')
    ]);

    const metrics = await metricsRes.json();
    activeCases = await casesRes.json();
    activeAuditLogs = await auditRes.json();

    renderOverviewMetrics(metrics);
    renderPillars(metrics);
    renderCasesTable();
    renderAuditTable();
    renderLiveFeed();
    populateVoiceSelect();

    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.error('Data load error:', e);
  }
}

function renderOverviewMetrics(metrics) {
  document.getElementById('val-recovered-inr').textContent = `₹${metrics.total_recovered_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  document.getElementById('val-recovery-rate').textContent = `${metrics.recovery_rate_pct}%`;
  document.getElementById('val-atrisk-inr').textContent = `₹${metrics.total_at_risk_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
  document.getElementById('val-total-cases').textContent = metrics.total_cases;
  document.getElementById('val-recovered-count').textContent = metrics.recovered_count;
  document.getElementById('val-ptp-compliance').textContent = `${metrics.ptp_count + metrics.halted_compliance_count}`;
  document.getElementById('val-ptp-count').textContent = metrics.ptp_count;
  document.getElementById('val-halted-count').textContent = metrics.halted_compliance_count;
  document.getElementById('badge-at-risk').textContent = activeCases.filter(c => c.status === 'at_risk').length;
  document.getElementById('audit-count-pill').textContent = `${activeAuditLogs.length} Audit Blocks Verified`;
}

function renderPillars(metrics) {
  const container = document.getElementById('pillars-container');
  if (!container) return;

  const pillarMeta = [
    { key: 'payment_degradation', title: '1. Payment Degradation & Root Cause', icon: 'activity', desc: 'Soft vs hard decline & bank downtime detector' },
    { key: 'checkout_dropoff', title: '2. Checkout Drop-Off Rescue', icon: 'shopping-cart', desc: 'Dynamic 1-click Razorpay UPI intent deep-links' },
    { key: 'failed_subscription', title: '3. Failed Subscription Dunning', icon: 'refresh-cw', desc: 'Involuntary churn & card swap dunning' },
    { key: 'b2b_receivables', title: '4. B2B Receivables Chaser', icon: 'file-text', desc: 'Compliant tiered invoice escalation' },
    { key: 'mandate_failure', title: '5. Mandate Retry Sequencer', icon: 'calendar', desc: 'Payday cycles & bank success heatmaps' },
  ];

  container.innerHTML = pillarMeta.map(p => {
    const data = metrics.category_breakdown[p.key] || { at_risk: 0, recovered: 0, count: 0, recovered_count: 0 };
    const winRate = data.at_risk > 0 ? ((data.recovered / data.at_risk) * 100).toFixed(1) : 0;

    return `
      <div class="pillar-card">
        <div class="pillar-head">
          <div class="pillar-icon-box"><i data-lucide="${p.icon}"></i></div>
          <div>
            <div class="pillar-title">${p.title}</div>
            <small class="text-muted">${p.desc}</small>
          </div>
        </div>
        <div class="pillar-stats">
          <div>At-Risk: <strong>₹${data.at_risk.toLocaleString('en-IN')}</strong></div>
          <div>Recovered: <strong class="text-success">₹${data.recovered.toLocaleString('en-IN')} (${winRate}%)</strong></div>
        </div>
      </div>
    `;
  }).join('');
}

function renderCasesTable() {
  const tbody = document.getElementById('cases-table-body');
  const catFilter = document.getElementById('filter-category').value;
  const statusFilter = document.getElementById('filter-status').value;

  let filtered = activeCases;
  if (catFilter) filtered = filtered.filter(c => c.transaction.category === catFilter);
  if (statusFilter) filtered = filtered.filter(c => c.status === statusFilter);

  tbody.innerHTML = filtered.map(c => {
    const statusBadge = getStatusBadge(c.status);
    const diagnosis = c.diagnostic ? c.diagnostic.root_cause : '<span class="text-muted">Awaiting Diagnosis</span>';
    const channel = c.transaction.payment_method.toUpperCase();

    return `
      <tr>
        <td><strong>${c.id}</strong></td>
        <td>
          <div><strong>${c.customer.name}</strong></div>
          <small class="text-muted">${c.customer.phone} • ${channel}</small>
        </td>
        <td>
          <span class="badge badge-outline">${formatCategory(c.transaction.category)}</span>
          <div class="text-muted" style="font-size:0.75rem; margin-top:2px;">${c.transaction.error_code || 'N/A'}</div>
        </td>
        <td><strong>₹${c.transaction.amount_inr.toLocaleString('en-IN')}</strong></td>
        <td style="max-width:240px; font-size:0.8rem;">${diagnosis}</td>
        <td><span class="badge ${statusBadge}">${c.status.replace('_', ' ').toUpperCase()}</span></td>
        <td>
          <button class="case-row-btn" onclick="openCaseModal('${c.id}')">
            Inspect
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderAuditTable() {
  const tbody = document.getElementById('audit-table-body');
  if (!tbody) return;

  tbody.innerHTML = activeAuditLogs.map(l => `
    <tr>
      <td class="mono-text">${l.timestamp.substring(11, 19)}</td>
      <td><strong>${l.case_id}</strong></td>
      <td><span class="badge badge-primary">${l.event_type}</span></td>
      <td>${l.actor}</td>
      <td style="font-size:0.8rem; max-width:320px;">${JSON.stringify(l.details)}</td>
      <td class="mono-text" title="${l.hash_signature}">${l.hash_signature.substring(0, 12)}...</td>
    </tr>
  `).join('');
}

function renderLiveFeed() {
  const feed = document.getElementById('live-activity-stream');
  if (!feed) return;

  feed.innerHTML = activeAuditLogs.slice(0, 8).map(l => `
    <div class="feed-item">
      <span class="feed-time">${l.timestamp.substring(11, 19)}</span>
      <div>
        <span class="feed-event">[${l.event_type}]</span>
        <span>Case ${l.case_id} by <em>${l.actor}</em></span>
      </div>
    </div>
  `).join('');
}

function populateVoiceSelect() {
  const select = document.getElementById('voice-case-select');
  if (!select) return;

  select.innerHTML = activeCases.map(c => `
    <option value="${c.id}">${c.id} - ${c.customer.name} (₹${c.transaction.amount_inr}) [${formatCategory(c.transaction.category)}]</option>
  `).join('');

  if (activeCases.length > 0 && !currentVoiceCaseId) {
    currentVoiceCaseId = activeCases[0].id;
    loadVoiceScript(currentVoiceCaseId);
  }
}

async function loadVoiceScript(caseId) {
  currentVoiceCaseId = caseId;
  try {
    const res = await fetch(`/api/voice/${caseId}/script`);
    const data = await res.json();
    document.getElementById('voice-script-text').textContent = data.script_hinglish;

    // Update WhatsApp Mockup preview
    const c = activeCases.find(x => x.id === caseId);
    if (c) {
      document.getElementById('wa-bubble-text').textContent = `Namaste ${c.customer.name}! Aapke ₹${c.transaction.amount_inr} payment ke regarding 1-click Razorpay UPI link dispatch kiya gaya hai:`;
      document.getElementById('wa-amount').textContent = c.transaction.amount_inr.toLocaleString('en-IN');
      document.getElementById('wa-link-cta').style.display = 'flex';
      document.getElementById('wa-link-cta').onclick = () => window.open(data.payment_link, '_blank');
    }
  } catch (e) {
    console.error(e);
  }
}

async function sendVoiceTurn(utterance) {
  if (!currentVoiceCaseId) return;

  try {
    const res = await fetch('/api/voice/turn', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: currentVoiceCaseId, user_utterance: utterance })
    });
    const data = await res.json();

    const replyBox = document.getElementById('voice-bot-reply');
    replyBox.style.display = 'block';
    document.getElementById('bot-reply-text').textContent = `"${data.bot_reply}"`;
    document.getElementById('voice-action-badge').innerHTML = `
      <span class="badge badge-success">Intent: ${data.intent}</span>
      <span class="badge badge-primary">Action: ${data.action_taken}</span>
    `;

    // Speak bot reply
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(data.bot_reply);
      u.lang = 'hi-IN';
      window.speechSynthesis.speak(u);
    }

    loadAllData();
  } catch (e) {
    alert('Voice turn error: ' + e);
  }
}

window.openCaseModal = function(caseId) {
  const c = activeCases.find(x => x.id === caseId);
  if (!c) return;

  const modal = document.getElementById('case-modal');
  const title = document.getElementById('modal-case-title');
  const body = document.getElementById('modal-case-content');

  title.textContent = `Case Deep Dive: ${c.id} (${c.customer.name})`;
  body.innerHTML = `
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px;">
      <div>
        <p class="text-muted"><small>Customer Details</small></p>
        <p><strong>${c.customer.name}</strong> (${c.customer.email})</p>
        <p>${c.customer.phone} • Lang: ${c.customer.language_preference}</p>
        ${c.customer.company_name ? `<p>Company: ${c.customer.company_name}</p>` : ''}
      </div>
      <div>
        <p class="text-muted"><small>Transaction Context</small></p>
        <p><strong>Amount: ₹${c.transaction.amount_inr.toLocaleString('en-IN')}</strong></p>
        <p>Category: ${formatCategory(c.transaction.category)}</p>
        <p>Error: ${c.transaction.error_code || 'None'}</p>
      </div>
    </div>

    <div class="card" style="background:var(--bg-subtle);">
      <h4>🧠 Diagnostic & Root-Cause Analysis</h4>
      <p><strong>Decline Type:</strong> ${c.diagnostic ? c.diagnostic.decline_type : 'N/A'}</p>
      <p><strong>Root Cause:</strong> ${c.diagnostic ? c.diagnostic.root_cause : 'N/A'}</p>
      <p><strong>Recommended Strategy:</strong> ${c.diagnostic ? c.diagnostic.recommended_strategy : 'N/A'}</p>
    </div>

    <div class="card" style="background:var(--bg-subtle); margin-top:12px;">
      <h4>⚡ Active Intervention & Razorpay Execution</h4>
      <p><strong>Strategy:</strong> ${c.active_intervention ? c.active_intervention.strategy_name : 'None'}</p>
      <p><strong>Description:</strong> ${c.active_intervention ? c.active_intervention.action_description : 'None'}</p>
      <p><strong>Payload:</strong> <pre class="mono-text" style="background:#090d16; padding:8px; border-radius:6px; overflow-x:auto;">${JSON.stringify(c.active_intervention ? c.active_intervention.payload : {}, null, 2)}</pre></p>
    </div>

    <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:16px;">
      <button class="btn btn-primary" onclick="processCaseDirect('${c.id}')">Execute Single Recovery</button>
    </div>
  `;

  modal.style.display = 'flex';
};

window.processCaseDirect = async function(caseId) {
  try {
    const res = await fetch(`/api/recovery/cases/${caseId}/process`, { method: 'POST' });
    const data = await res.json();
    alert(`Case ${caseId} processed. Status: ${data.status}`);
    document.getElementById('case-modal').style.display = 'none';
    loadAllData();
  } catch (e) {
    alert('Processing error: ' + e);
  }
};

function getStatusBadge(status) {
  switch (status) {
    case 'recovered': return 'badge-success';
    case 'at_risk': return 'badge-danger';
    case 'ptp_committed': return 'badge-warning';
    case 'halted_compliance':
    case 'halted_dispute': return 'badge-warning';
    default: return 'badge-primary';
  }
}

function formatCategory(cat) {
  return cat.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}
