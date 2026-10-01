// Calendar View JavaScript Component
class MeetingCalendar {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentDate = new Date();
  }

  async init() {
    if (!this.container) return;
    const meetings = await api.get('/meetings/');
    this.render(meetings);
  }

  render(meetings) {
    let html = `
      <div class="calendar-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
        <h3>Meeting Calendar (${this.currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })})</h3>
        <a href="/meetings/create/" class="btn btn-primary">+ Schedule Meeting</a>
      </div>
      <div class="calendar-grid" style="display:grid;grid-template-columns:repeat(7, 1fr);gap:10px;">
    `;

    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    days.forEach(d => {
      html += `<div style="text-align:center;font-weight:700;color:var(--text-muted);padding:8px;background:rgba(255,255,255,0.03);border-radius:6px;">${d}</div>`;
    });

    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
      html += `<div style="min-height:90px;background:rgba(0,0,0,0.2);border-radius:8px;"></div>`;
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayMeetings = meetings.filter(m => m.date === dateStr);

      html += `
        <div style="min-height:90px;background:var(--bg-card);border:1px solid var(--border-color);border-radius:8px;padding:6px;">
          <div style="font-weight:bold;font-size:0.85rem;color:var(--text-muted);margin-bottom:4px;">${day}</div>
      `;

      dayMeetings.forEach(m => {
        html += `
          <a href="/meetings/${m.id}/" style="display:block;background:rgba(99,102,241,0.2);color:#fff;font-size:0.75rem;padding:4px 6px;border-radius:4px;margin-bottom:4px;text-decoration:none;border-left:3px solid var(--primary);overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">
            ${m.start_time.substring(0,5)} ${m.title}
          </a>
        `;
      });

      html += `</div>`;
    }

    html += `</div>`;
    this.container.innerHTML = html;
  }
}
