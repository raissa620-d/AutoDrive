const modal = document.getElementById('authModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModal = document.getElementById('closeModal');
    const loginTab = document.getElementById('loginTab');
    const registerTab = document.getElementById('registerTab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Ouvrir modale
    openModalBtn.onclick = () => modal.style.display = 'flex';
    // Fermer modale
    closeModal.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target === modal) modal.style.display = 'none'; };

    // Changer d'onglet
    loginTab.onclick = () => {
      loginTab.classList.add('active');
      registerTab.classList.remove('active');
      loginForm.classList.add('active');
      registerForm.classList.remove('active');
    };

    registerTab.onclick = () => {
      registerTab.classList.add('active');
      loginTab.classList.remove('active');
      registerForm.classList.add('active');
      loginForm.classList.remove('active');
    };
      // Modales
        const authModal = document.getElementById('authModal');
        const vehiclesModal = document.getElementById('vehiclesModal');

// Ouvrir modale véhicules
        openVehiclesBtn.onclick = () => vehiclesModal.style.display = 'flex';

        // Fermer modales
        closeModal.onclick = () => authModal.style.display = 'none';
        closeVehiclesModal.onclick = () => vehiclesModal.style.display = 'none';

        window.onclick = (e) => {
            if (e.target === authModal) authModal.style.display = 'none';
            if (e.target === vehiclesModal) vehiclesModal.style.display = 'none';
        };
       // Boutons de fermeture
        const closeVehiclesModal = document.getElementById('closeVehiclesModal');
        const closeAuthModal = document.getElementById('closeAuthModal');

document.addEventListener("DOMContentLoaded", () => {
      const openVehiclesBtn = document.getElementById('openVehiclesBtn');
      const vehiclesModal = document.getElementById('vehiclesModal');
      const closeVehiclesModal = document.getElementById('closeVehiclesModal');

      const modal = document.getElementById('authModal');
      const openModalBtn = document.getElementById('openModalBtn');

      openVehiclesBtn.onclick = () => vehiclesModal.style.display = 'flex';
      closeVehiclesModal.onclick = () => vehiclesModal.style.display = 'none';

      window.onclick = (e) => {
        if (e.target === vehiclesModal) vehiclesModal.style.display = 'none';
      };
    });