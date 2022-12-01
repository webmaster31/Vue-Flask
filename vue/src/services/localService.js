export default {
  setItem(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },
  removeItem(key) {
    localStorage.removeItem(key);
  },
  getItem(key) {
    return JSON.parse(localStorage.getItem(key));
  },
  clear() {
    localStorage.clear();
  }
}