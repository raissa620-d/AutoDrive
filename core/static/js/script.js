
  /* ----- MAP ----- */
  (function () {
    const el = document.getElementById("map-data");
    if (!el) return;

    const points = JSON.parse(el.textContent);
    const center = [6.1319, 1.2228];
    const map = L.map("accueil-map").setView(center, points.length ? 12 : 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19
    }).addTo(map);

    if (!points.length) {
      L.marker(center).addTo(map).bindPopup("Aucun véhicule géolocalisé.");
      return;
    }

    points.forEach(p => {
      const popup =
        `<strong>${p.label}</strong><br>${p.ville || ""} ${p.adresse || ""}<br>${Number(p.prix_jour || 0).toLocaleString("fr-FR")} FCFA/jour`;
      L.marker([p.lat, p.lng]).addTo(map).bindPopup(popup);
    });
  })();


  /* ----- MODAL AUTH ----- */
  document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("authModal");
    const openModalBtn = document.getElementById("openModalBtn");
    const closeModal = document.getElementById("closeModal");
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    // Vérifier que tous les éléments existent
    if (!modal || !openModalBtn || !closeModal || !loginTab || !registerTab || !loginForm || !registerForm) {
      console.error("Un ou plusieurs éléments du modal sont introuvables");
      return;
    }

    // Ouvrir la modale (par défaut sur l'onglet connexion)
    openModalBtn.onclick = () => {
      modal.style.display = "flex";
      // S'assurer que l'onglet connexion est actif
      loginTab.click();
    };

    // Fermer la modale
    closeModal.onclick = () => {
      modal.style.display = "none";
    };

    // Fermer en cliquant à l'extérieur
    window.onclick = (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    };

    // Onglet Connexion
    loginTab.onclick = () => {
      loginTab.classList.add("active");
      registerTab.classList.remove("active");
      loginForm.classList.add("active");
      registerForm.classList.remove("active");
    };

    // Onglet Inscription
    registerTab.onclick = () => {
      registerTab.classList.add("active");
      loginTab.classList.remove("active");
      registerForm.classList.add("active");
      loginForm.classList.remove("active");
    };
  }