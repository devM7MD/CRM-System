// Copied from Atlas Service js/app.js
// ... existing code ... 

document.addEventListener("DOMContentLoaded", () => {
  // Load navbar and footer
  const navbarContainer = document.getElementById("navbar-container");
  const footerContainer = document.getElementById("footer-container");

  if (navbarContainer) {
    fetch("navbar.html")
      .then((response) => response.text())
      .then((html) => {
        navbarContainer.innerHTML = html;

        // Initialize mobile menu after navbar is loaded
        initializeMobileMenu();
      })
      .catch((error) => console.error("Error loading navbar:", error));
  }

  if (footerContainer) {
    fetch("footer.html")
      .then((response) => response.text())
      .then((html) => {
        footerContainer.innerHTML = html;
      })
      .catch((error) => console.error("Error loading footer:", error));
  }

  // Initialize gradient animation
  initGradientAnimation();

  // Initialize i18n system if available
  if (window.Atlas && window.Atlas.i18n) {
    window.Atlas.i18n.init();
  }
});

// Function to initialize mobile menu
function initializeMobileMenu() {
  // Desktop dropdowns
  initializeDesktopDropdowns();

  // Mobile menu functionality
  const mobileMenuButton = document.getElementById("mobile-menu-button");
  const mobileMenu = document.getElementById("mobile-menu");
  const mobileMenuOverlay = document.getElementById("mobile-menu-overlay");
  const mobileMenuClose = document.getElementById("mobile-menu-close");

  // Mobile menu toggle
  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", function () {
      mobileMenu.classList.remove("translate-x-full");
      mobileMenuOverlay.classList.remove("hidden");
      mobileMenuButton.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden"; // Prevent scrolling
    });

    // Close mobile menu via X button
    if (mobileMenuClose) {
      mobileMenuClose.addEventListener("click", function () {
        mobileMenu.classList.add("translate-x-full");
        mobileMenuOverlay.classList.add("hidden");
        mobileMenuButton.setAttribute("aria-expanded", "false");
        document.body.style.overflow = ""; // Restore scrolling
      });
    }

    // Close mobile menu via overlay click
    if (mobileMenuOverlay) {
      mobileMenuOverlay.addEventListener("click", function () {
        mobileMenu.classList.add("translate-x-full");
        mobileMenuOverlay.classList.add("hidden");
        mobileMenuButton.setAttribute("aria-expanded", "false");
        document.body.style.overflow = ""; // Restore scrolling
      });
    }
  }

  // Initialize mobile submenus
  initializeMobileSubmenus();

  // Handle mobile links
  const mobileLinks = mobileMenu?.querySelectorAll("a:not([id])");
  if (mobileLinks) {
    mobileLinks.forEach((link) => {
      link.addEventListener("click", function () {
        // Close the mobile menu when a link is clicked
        mobileMenu.classList.add("translate-x-full");
        mobileMenuOverlay.classList.add("hidden");
        if (mobileMenuButton) {
          mobileMenuButton.setAttribute("aria-expanded", "false");
        }
        document.body.style.overflow = ""; // Restore scrolling
      });
    });
  }
}

// Function to initialize desktop dropdowns
function initializeDesktopDropdowns() {
  document
    .querySelectorAll(".desktop-dropdown-trigger")
    .forEach((dropdownContainer) => {
      const trigger = dropdownContainer.querySelector("button");
      const dropdown = dropdownContainer.querySelector(".desktop-dropdown");

      if (!trigger || !dropdown) return;

      // Track if the dropdown is open due to click
      let dropdownOpenedByClick = false;

      // Show dropdown on hover only if not already opened by click
      dropdownContainer.addEventListener("mouseenter", function () {
        if (!dropdownOpenedByClick) {
          dropdown.classList.add("active");
          trigger.setAttribute("aria-expanded", "true");
        }
      });

      // Hide dropdown when mouse leaves, but only if not opened by click
      dropdownContainer.addEventListener("mouseleave", function () {
        if (!dropdownOpenedByClick) {
          dropdown.classList.remove("active");
          trigger.setAttribute("aria-expanded", "false");
        }
      });

      // Toggle dropdown on click (for touch devices)
      trigger.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();

        const isActive = dropdown.classList.contains("active");

        if (isActive) {
          dropdown.classList.remove("active");
          trigger.setAttribute("aria-expanded", "false");
          dropdownOpenedByClick = false;
        } else {
          dropdown.classList.add("active");
          trigger.setAttribute("aria-expanded", "true");
          dropdownOpenedByClick = true;
        }
      });

      // Reset click state when clicking elsewhere
      document.addEventListener("click", function (event) {
        if (
          !trigger.contains(event.target) &&
          !dropdown.contains(event.target)
        ) {
          dropdownOpenedByClick = false;
          dropdown.classList.remove("active");
          trigger.setAttribute("aria-expanded", "false");
        }
      });
    });
}

// Function to initialize mobile submenus
function initializeMobileSubmenus() {
  // Mobile submenu toggles
  document.querySelectorAll(".mobile-submenu-trigger").forEach((trigger) => {
    const submenu = trigger.nextElementSibling;
    const icon = trigger.querySelector("svg");

    if (!submenu || !submenu.classList.contains("mobile-submenu")) return;

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      submenu.classList.toggle("hidden");

      if (icon) {
        icon.style.transform = submenu.classList.contains("hidden")
          ? ""
          : "rotate(180deg)";
      }
    });
  });

  // Mobile language selector
  const languageTrigger = document.querySelector(".mobile-language-trigger");
  const languageMenu = document.querySelector(".mobile-language-menu");
  const languageIcon = languageTrigger?.querySelector("svg");

  if (languageTrigger && languageMenu) {
    languageTrigger.addEventListener("click", function (e) {
      e.preventDefault();
      languageMenu.classList.toggle("hidden");

      if (languageIcon) {
        languageIcon.style.transform = languageMenu.classList.contains("hidden")
          ? ""
          : "rotate(180deg)";
      }
    });
  }
}

// Function to initialize gradient animation
function initGradientAnimation() {
  const canvas = document.getElementById("gradient-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  let gradient;
  let gradientX = 0;
  let gradientY = 0;
  let gradientSize = Math.max(canvas.width, canvas.height);

  // Create gradient
  function createGradient() {
    gradient = ctx.createRadialGradient(
      gradientX,
      gradientY,
      0,
      gradientX,
      gradientY,
      gradientSize
    );

    gradient.addColorStop(0, "rgba(245, 158, 11, 0.8)"); // amber-500
    gradient.addColorStop(0.5, "rgba(202, 138, 4, 0.5)"); // amber-600
    gradient.addColorStop(1, "rgba(161, 98, 7, 0.2)"); // amber-700
  }

  // Animate gradient
  function animate() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Move gradient position
    gradientX =
      canvas.width / 2 + Math.sin(Date.now() * 0.001) * canvas.width * 0.1;
    gradientY =
      canvas.height / 2 + Math.cos(Date.now() * 0.0015) * canvas.height * 0.1;

    // Create new gradient
    createGradient();

    // Fill with gradient
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Continue animation
    requestAnimationFrame(animate);
  }

  // Handle window resize

} 