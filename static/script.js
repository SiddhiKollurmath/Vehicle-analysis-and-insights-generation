document.addEventListener('DOMContentLoaded', () => {
  const themeIcon = document.getElementById('theme-icon');
  
  document.querySelector('.theme-toggle').addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      themeIcon.src = document.body.classList.contains('dark-mode') ? 'dark-icon.png' : 'light-icon.png';
  });

  document.querySelector('.search-bar').addEventListener('submit', (event) => {
      event.preventDefault();
      const query = document.getElementById('search-input').value;
      alert(`Searching for: ${query}`);
  });
});
