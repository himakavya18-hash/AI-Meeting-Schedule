// API Client Helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const api = {
  async request(endpoint, options = {}) {
    const url = `/api${endpoint}`;
    const headers = options.headers || {};
    
    // Add CSRF token for Django requests
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
      headers['X-CSRFToken'] = csrftoken;
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      if (response.status === 401) {
        if (!window.location.pathname.includes('/login/')) {
          window.location.href = '/login/';
        }
      }
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        let msg = data.error || data.detail || data.message;
        if (!msg && typeof data === 'object') {
          const keys = Object.keys(data);
          if (keys.length > 0) {
            const firstVal = data[keys[0]];
            msg = Array.isArray(firstVal) ? `${keys[0]}: ${firstVal.join(', ')}` : `${keys[0]}: ${firstVal}`;
          }
        }
        throw new Error(msg || `Server error (${response.status})`);
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, data) {
    const body = (data instanceof FormData) ? data : JSON.stringify(data);
    return this.request(endpoint, { method: 'POST', body });
  },

  put(endpoint, data) {
    const body = (data instanceof FormData) ? data : JSON.stringify(data);
    return this.request(endpoint, { method: 'PUT', body });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};
