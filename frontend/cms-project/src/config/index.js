export const APP_CONFIG = {
  appName: 'CMS Project',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  requestTimeout: 10000,
  version: '1.0.0',
}

export default APP_CONFIG
