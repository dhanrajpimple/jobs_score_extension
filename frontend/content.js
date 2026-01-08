(function() {
  if (document.getElementById('jm-widget')) return;

  const widget = document.createElement('div');
  widget.id = 'jm-widget';
  widget.innerHTML = `
    <style>
      #jm-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      }
      #jm-btn {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        display: flex;
        align-items: center;
        gap: 6px;
      }
      #jm-btn:hover { transform: translateY(-2px); }
      #jm-btn:disabled { background: #6b7280; cursor: wait; }
      
      #jm-result {
        display: none;
        background: #0a0a0f;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        width: 290px;
        max-height: 420px;
        overflow-y: auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        animation: slideUp 0.2s ease;
      }
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .jm-verdict {
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
      }
      .jm-verdict.apply {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%);
        border: 1px solid rgba(34, 197, 94, 0.3);
      }
      .jm-verdict.skip {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
      }
      .jm-verdict-text { font-size: 18px; font-weight: 700; letter-spacing: 1px; }
      .jm-verdict.apply .jm-verdict-text { color: #22c55e; }
      .jm-verdict.skip .jm-verdict-text { color: #ef4444; }
      .jm-score { font-size: 28px; font-weight: 700; }
      .jm-verdict.apply .jm-score { color: #4ade80; }
      .jm-verdict.skip .jm-score { color: #f87171; }
      
      .jm-exp-flag {
        padding: 8px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 11px;
        font-weight: 500;
      }
      .jm-exp-flag.green {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #86efac;
      }
      .jm-exp-flag.yellow {
        background: rgba(234, 179, 8, 0.15);
        border: 1px solid rgba(234, 179, 8, 0.3);
        color: #fde047;
      }
      .jm-exp-flag.red {
        background: rgba(239, 68, 68, 0.2);
        border: 2px solid rgba(239, 68, 68, 0.5);
        color: #fca5a5;
      }
      
      .jm-row {
        background: rgba(255,255,255,0.03);
        padding: 6px 8px;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 2px solid #6366f1;
      }
      .jm-row.qual { border-left-color: #22c55e; }
      .jm-row.skill { border-left-color: #3b82f6; }
      .jm-label { font-size: 9px; color: #6b7280; text-transform: uppercase; margin-bottom: 2px; }
      .jm-value { font-size: 10px; color: #d1d5db; line-height: 1.3; }
      
      .jm-skills {
        font-size: 9px;
        padding: 6px;
        border-radius: 5px;
        margin-bottom: 5px;
        display: none;
      }
      .jm-skills.matched { background: rgba(34, 197, 94, 0.1); color: #86efac; }
      .jm-skills.missing { background: rgba(239, 68, 68, 0.1); color: #fca5a5; }
      .jm-tag {
        display: inline-block;
        padding: 2px 4px;
        margin: 1px;
        border-radius: 3px;
        font-size: 9px;
        background: rgba(255,255,255,0.1);
      }
      
      .jm-action {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 5px;
        padding: 8px;
        margin-bottom: 8px;
      }
      .jm-action .jm-label { color: #a5b4fc; }
      .jm-action .jm-value { color: #c7d2fe; }
      
      #jm-close {
        width: 100%;
        padding: 8px;
        background: rgba(255,255,255,0.1);
        border: none;
        border-radius: 5px;
        color: #9ca3af;
        font-size: 11px;
        cursor: pointer;
      }
      
      .jm-spinner {
        width: 12px; height: 12px;
        border: 2px solid rgba(255,255,255,0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: none;
      }
      @keyframes spin { to { transform: rotate(360deg); } }
      
      #jm-error {
        display: none;
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        padding: 10px;
        border-radius: 8px;
        font-size: 11px;
        margin-bottom: 8px;
        max-width: 280px;
      }
      #jm-hint { font-size: 9px; color: #6b7280; text-align: center; margin-top: 6px; }
    </style>
    
    <div id="jm-error"></div>
    
    <div id="jm-result">
      <div class="jm-verdict" id="jm-verdict-card">
        <div class="jm-verdict-text" id="jm-verdict"></div>
        <div class="jm-score" id="jm-score">--%</div>
      </div>
      
      <div class="jm-exp-flag" id="jm-exp-flag"></div>
      
      <div class="jm-row qual">
        <div class="jm-label">🎓 Qualification</div>
        <div class="jm-value" id="jm-qual"></div>
      </div>
      <div class="jm-row skill">
        <div class="jm-label">💻 Skills</div>
        <div class="jm-value" id="jm-skill"></div>
      </div>
      
      <div class="jm-skills matched" id="jm-matched"></div>
      <div class="jm-skills missing" id="jm-missing"></div>
      
      <div class="jm-action">
        <div class="jm-label">💡 Action</div>
        <div class="jm-value" id="jm-action"></div>
      </div>
      
      <button id="jm-close">Close</button>
    </div>
    
    <button id="jm-btn">
      <span id="jm-btn-text">⚡ Check Match</span>
      <div class="jm-spinner" id="jm-spinner"></div>
    </button>
    <div id="jm-hint">Select text first</div>
  `;
  
  document.body.appendChild(widget);
  
  const btn = document.getElementById('jm-btn');
  const btnText = document.getElementById('jm-btn-text');
  const spinner = document.getElementById('jm-spinner');
  const resultDiv = document.getElementById('jm-result');
  const errorDiv = document.getElementById('jm-error');
  
  btn.addEventListener('click', async () => {
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.style.display = 'inline-block';
    
    try {
      const text = window.getSelection()?.toString().trim();
      if (!text || text.length < 30) {
        throw new Error('Select job description text (min 30 chars)');
      }
      
      const res = await chrome.runtime.sendMessage({
        action: 'calculateScore',
        jobDescription: text
      });
      
      if (res.error) throw new Error(res.error);
      
      // Verdict
      const isApply = res.verdict === 'APPLY';
      document.getElementById('jm-verdict-card').className = `jm-verdict ${isApply ? 'apply' : 'skip'}`;
      document.getElementById('jm-verdict').textContent = res.verdict;
      document.getElementById('jm-score').textContent = `${res.score}%`;
      
      // Experience flag
      const expFlag = document.getElementById('jm-exp-flag');
      expFlag.textContent = res.experienceMatch;
      expFlag.className = 'jm-exp-flag';
      expFlag.classList.add(res.experienceFlag.toLowerCase());
      
      // Info
      document.getElementById('jm-qual').textContent = res.qualificationMatch || '-';
      document.getElementById('jm-skill').textContent = res.skillsMatch || '-';
      document.getElementById('jm-action').textContent = res.action || '-';
      
      // Skills
      const matched = document.getElementById('jm-matched');
      const missing = document.getElementById('jm-missing');
      
      if (res.matchedSkills?.length) {
        matched.innerHTML = `<strong>✅ Your Skills:</strong> ` +
          res.matchedSkills.map(s => `<span class="jm-tag">${s}</span>`).join('');
        matched.style.display = 'block';
      } else matched.style.display = 'none';
      
      if (res.missingSkills?.length) {
        missing.innerHTML = `<strong>📚 To Learn:</strong> ` +
          res.missingSkills.map(s => `<span class="jm-tag">${s}</span>`).join('');
        missing.style.display = 'block';
      } else missing.style.display = 'none';
      
      resultDiv.style.display = 'block';
      
    } catch (err) {
      errorDiv.textContent = err.message;
      errorDiv.style.display = 'block';
      setTimeout(() => errorDiv.style.display = 'none', 4000);
    } finally {
      btn.disabled = false;
      btnText.style.display = 'inline';
      spinner.style.display = 'none';
    }
  });
  
  document.getElementById('jm-close').addEventListener('click', () => {
    resultDiv.style.display = 'none';
  });
})();

new MutationObserver(() => {
  if (!document.getElementById('jm-widget')) location.reload();
}).observe(document.body, { childList: true, subtree: true });
