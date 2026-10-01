// AI Extractor & Transcript Analysis Helper
const aiExtractor = {
  async triggerAnalysis(transcriptId) {
    const loader = document.getElementById('ai-loading-indicator');
    if (loader) loader.style.display = 'block';

    try {
      const res = await api.post(`/actions/transcripts/${transcriptId}/analyze/`, {});
      if (loader) loader.style.display = 'none';
      return res;
    } catch (err) {
      if (loader) loader.style.display = 'none';
      alert('AI Extraction Error: ' + err.message);
      throw err;
    }
  },

  async loadMeetingReport(meetingId) {
    return await api.get(`/actions/meetings/${meetingId}/analysis/`);
  },

  async updateActionStatus(actionId, status) {
    try {
      return await api.put(`/actions/${actionId}/`, { status });
    } catch (e) {
      alert('Failed to update action status: ' + e.message);
    }
  },

  async resolveQuestion(questionId, status, notes = '') {
    try {
      return await api.put(`/actions/questions/${questionId}/`, { status, resolution_notes: notes });
    } catch (e) {
      alert('Failed to resolve question: ' + e.message);
    }
  }
};
