const API_URL = 'http://localhost:8000/score';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'calculateScore') {
    handleScore(request.jobDescription)
      .then(sendResponse)
      .catch(err => sendResponse({ error: err.message }));
    return true;
  }
});

async function handleScore(jobDescription) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_description: jobDescription })
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Error: ${response.status}`);
  }

  const data = await response.json();
  
  return {
    score: data.match_score,
    verdict: data.verdict,
    experienceMatch: data.experience_match,
    experienceFlag: data.experience_flag,
    qualificationMatch: data.qualification_match,
    skillsMatch: data.skills_match,
    matchedSkills: data.matched_skills,
    missingSkills: data.missing_skills,
    action: data.action
  };
}
