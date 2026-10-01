// Authentication & Firebase Helper
const authService = {
  async getCurrentUser() {
    try {
      const user = await api.get('/accounts/me/');
      return user;
    } catch (e) {
      return null;
    }
  },

  async loginWithEmailPassword(identifier, password) {
    try {
      const res = await api.post('/accounts/login/', {
        email: identifier,
        password: password
      });
      const urlParams = new URLSearchParams(window.location.search);
      const nextUrl = urlParams.get('next') || '/dashboard/';
      window.location.href = nextUrl;
      return res;
    } catch (e) {
      throw e;
    }
  },

  async registerUser(userData) {
    try {
      const res = await api.post('/accounts/register/', userData);
      const urlParams = new URLSearchParams(window.location.search);
      const nextUrl = urlParams.get('next') || '/dashboard/';
      window.location.href = nextUrl;
      return res;
    } catch (e) {
      throw e;
    }
  },

  async loginWithDemoUser(username, role = 'Software Engineer') {
    try {
      const res = await api.post('/accounts/demo-login/', {
        username: username,
        email: `${username.toLowerCase()}@company.com`,
        first_name: username,
        job_role: role
      });
      const urlParams = new URLSearchParams(window.location.search);
      const nextUrl = urlParams.get('next') || '/dashboard/';
      window.location.href = nextUrl;
    } catch (e) {
      alert('Demo Login Error: ' + e.message);
    }
  },

  async loginWithFirebaseToken(idToken) {
    try {
      const res = await api.post('/accounts/firebase-login/', { id_token: idToken });
      window.location.href = '/dashboard/';
    } catch (e) {
      alert('Firebase Login Error: ' + e.message);
    }
  },

  async logout() {
    try {
      await api.post('/accounts/logout/');
    } catch (e) {
      console.warn('Logout warning:', e);
    }
    window.location.href = '/login/';
  }
};
