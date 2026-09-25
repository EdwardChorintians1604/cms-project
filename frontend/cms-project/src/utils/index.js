export const formatDate = (dateString, options = {}) => {
  if (!dateString) return ''
  const defaultOptions = { year: 'numeric', month: 'short', day: 'numeric', ...options }
  return new Date(dateString).toLocaleDateString('id-ID', defaultOptions)
}

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export const storage = {
  get: (key) => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (e) {
      console.error('Error reading localStorage key:', key, e)
      return null
    }
  },
  set: (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (e) {
      console.error('Error setting localStorage key:', key, e)
    }
  },
  remove: (key) => {
    localStorage.removeItem(key)
  },
}
