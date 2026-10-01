// Main Application Logic
document.addEventListener('DOMContentLoaded', async () => {
  // Check auth user
  const currentUser = await authService.getCurrentUser();
  if (currentUser) {
    updateUserUI(currentUser);
  } else if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login/';
    return;
  }

  // Handle Notifications Badge
  loadNotificationsBadge();
});

function updateUserUI(user) {
  const nameEls = document.querySelectorAll('.user-name-display');
  const roleEls = document.querySelectorAll('.user-role-display');
  const avatarEls = document.querySelectorAll('.user-avatar-display');

  nameEls.forEach(el => el.textContent = user.full_name || user.username);
  roleEls.forEach(el => el.textContent = `${user.job_role} • ${user.department}`);
  avatarEls.forEach(el => {
    if (user.avatar_url) {
      el.innerHTML = `<img src="${user.avatar_url}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
    } else {
      const initials = (user.first_name ? user.first_name[0] : user.username[0]).toUpperCase();
      el.textContent = initials;
    }
  });
}

async function loadNotificationsBadge() {
  try {
    const res = await api.get('/notifications/');
    const badge = document.getElementById('notification-badge');
    if (badge) {
      if (res.unread_count > 0) {
        badge.textContent = res.unread_count;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }
    }
  } catch (e) {
    // Ignore if not logged in
  }
}
