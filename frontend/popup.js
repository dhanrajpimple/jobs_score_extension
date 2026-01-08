document.addEventListener('DOMContentLoaded', () => {
  const checkBtn = document.getElementById('checkBtn');
  const loading = document.getElementById('loading');
  const result = document.getElementById('result');
  const verdictCard = document.getElementById('verdictCard');
  const verdictText = document.getElementById('verdictText');
  const scoreDiv = document.getElementById('score');
  const expFlag = document.getElementById('expFlag');
  const qualMatch = document.getElementById('qualMatch');
  const skillsMatch = document.getElementById('skillsMatch');
  const matchedSkills = document.getElementById('matchedSkills');
  const missingSkills = document.getElementById('missingSkills');
  const actionText = document.getElementById('actionText');
  const errorDiv = document.getElementById('error');

  checkBtn.addEventListener('click', async () => {
    result.style.display = 'none';
    errorDiv.style.display = 'none';
    loading.style.display = 'block';
    checkBtn.disabled = true;

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) throw new Error('Cannot access tab');

      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection()?.toString().trim() || ''
      });

      const selectedText = results?.[0]?.result;
      if (!selectedText || selectedText.length < 30) {
        throw new Error('Select job description text first (minimum 30 characters)');
      }

      const response = await chrome.runtime.sendMessage({
        action: 'calculateScore',
        jobDescription: selectedText
      });

      if (response.error) throw new Error(response.error);

      // Verdict
      const isApply = response.verdict === 'APPLY';
      verdictCard.className = `verdict-card ${isApply ? 'verdict-apply' : 'verdict-skip'}`;
      verdictText.textContent = response.verdict;
      scoreDiv.textContent = `${response.score}%`;

      // Experience flag with color
      expFlag.textContent = response.experienceMatch;
      expFlag.className = 'exp-flag';
      if (response.experienceFlag === 'GREEN') {
        expFlag.classList.add('green');
      } else if (response.experienceFlag === 'YELLOW') {
        expFlag.classList.add('yellow');
      } else {
        expFlag.classList.add('red');
      }

      // Other info
      qualMatch.textContent = response.qualificationMatch || '-';
      skillsMatch.textContent = response.skillsMatch || '-';
      actionText.textContent = response.action || '-';

      // Skills
      if (response.matchedSkills?.length) {
        matchedSkills.innerHTML = `<strong>✅ Your Skills:</strong>` +
          response.matchedSkills.map(s => `<span class="skill-tag">${s}</span>`).join('');
        matchedSkills.style.display = 'block';
      } else {
        matchedSkills.style.display = 'none';
      }

      if (response.missingSkills?.length) {
        missingSkills.innerHTML = `<strong>📚 To Learn:</strong>` +
          response.missingSkills.map(s => `<span class="skill-tag">${s}</span>`).join('');
        missingSkills.style.display = 'block';
      } else {
        missingSkills.style.display = 'none';
      }

      result.style.display = 'block';

    } catch (err) {
      errorDiv.textContent = err.message;
      errorDiv.style.display = 'block';
    } finally {
      loading.style.display = 'none';
      checkBtn.disabled = false;
    }
  });
});
