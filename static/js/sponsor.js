/**
* Template Name: Evently
* Template URL: https://bootstrapmade.com/evently-bootstrap-events-template/
* Updated: Jul 19 2025 with Bootstrap v5.3.7
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function() {
  "use strict";

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('#header');
    if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /**
   * Mobile nav toggle
   */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToogle() {
    document.querySelector('body').classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }
  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
  }

  /**
   * Hide mobile nav on same-page/hash links
   */
  document.querySelectorAll('#navmenu a').forEach(navmenu => {
    navmenu.addEventListener('click', () => {
      if (document.querySelector('.mobile-nav-active')) {
        mobileNavToogle();
      }
    });

  });

  /**
   * Toggle mobile nav dropdowns
   */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
    navmenu.addEventListener('click', function(e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /**
   * Preloader
   */
  document.addEventListener("DOMContentLoaded", function () {
  const preloader = document.getElementById("preloader");
  const content = document.getElementById("content");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(theme) {
    document.body.classList.remove("light-mode", "dark-mode");
    document.body.classList.add(theme);
    localStorage.setItem("theme", theme);
  }

  // Init theme (system default or saved)
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    applyTheme(prefersDark.matches ? "dark-mode" : "light-mode");
  }

  // Listen for system theme change if no manual override
  prefersDark.addEventListener("change", (e) => {
    if (!localStorage.getItem("theme")) {
      applyTheme(e.matches ? "dark-mode" : "light-mode");
    }
  });

  // Manual toggle button
  const toggleBtn = document.getElementById("theme-toggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      if (document.body.classList.contains("dark-mode")) {
        applyTheme("light-mode");
      } else {
        applyTheme("dark-mode");
      }
    });
  }

  // Preloader fade-out after page loads
  window.addEventListener("load", function () {
    setTimeout(() => {
      if (preloader) preloader.classList.add("fade-out");
      if (content) content.style.display = "block";
    }, 800);
  });
});


  // Initialize AOS
  AOS.init({
      duration: 800,
      once: true
  });

  /**
   * Scroll top button
   */
  let scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (scrollTop) {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }
  }
  scrollTop.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /**
   * Countdown timer
   */
  function updateCountDown(countDownItem) {
    const timeleft = new Date(countDownItem.getAttribute('data-count')).getTime() - new Date().getTime();

    const days = Math.floor(timeleft / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeleft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeleft % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeleft % (1000 * 60)) / 1000);

    const daysElement = countDownItem.querySelector('.count-days');
    const hoursElement = countDownItem.querySelector('.count-hours');
    const minutesElement = countDownItem.querySelector('.count-minutes');
    const secondsElement = countDownItem.querySelector('.count-seconds');

    if (daysElement) daysElement.innerHTML = days;
    if (hoursElement) hoursElement.innerHTML = hours;
    if (minutesElement) minutesElement.innerHTML = minutes;
    if (secondsElement) secondsElement.innerHTML = seconds;

  }

  document.querySelectorAll('.countdown').forEach(function(countDownItem) {
    updateCountDown(countDownItem);
    setInterval(function() {
      updateCountDown(countDownItem);
    }, 1000);
  });

  /**
   * Initiate Pure Counter
   */
  new PureCounter();

  /**
   * Init swiper sliders
   */
  function initSwiper() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  }

  window.addEventListener("load", initSwiper);

  /**
   * Initiate glightbox
   */
  const glightbox = GLightbox({
    selector: '.glightbox'
  });

  /*
   * Pricing Toggle
   */

  const pricingContainers = document.querySelectorAll('.pricing-toggle-container');

  pricingContainers.forEach(function(container) {
    const pricingSwitch = container.querySelector('.pricing-toggle input[type="checkbox"]');
    const monthlyText = container.querySelector('.monthly');
    const yearlyText = container.querySelector('.yearly');

    pricingSwitch.addEventListener('change', function() {
      const pricingItems = container.querySelectorAll('.pricing-item');

      if (this.checked) {
        monthlyText.classList.remove('active');
        yearlyText.classList.add('active');
        pricingItems.forEach(item => {
          item.classList.add('yearly-active');
        });
      } else {
        monthlyText.classList.add('active');
        yearlyText.classList.remove('active');
        pricingItems.forEach(item => {
          item.classList.remove('yearly-active');
        });
      }
    });
  });

})();

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("sponsor-registration-form");
  const submitBtn = document.getElementById("submit-btn");
  const alertContainer = document.getElementById("alert-container");

  // ----------------------------
  // 🛡️ CSRF helper
  // ----------------------------
  const getCookie = (name) => {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "="))
        return decodeURIComponent(cookie.substring(name.length + 1));
    }
    return null;
  };
  const csrftoken = getCookie("csrftoken");

  // ----------------------------
  // ⚠️ Alert handler
  // ----------------------------
  const showAlert = (message, type = "success") => {
    alertContainer.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>`;
    setTimeout(() => (alertContainer.innerHTML = ""), 8000);
  };

  // ----------------------------
  // 📁 File preview handler
  // ----------------------------
  const handlePreview = (inputId, previewId, imageOnly = false) => {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener("change", () => {
      preview.innerHTML = "";
      const file = input.files[0];
      if (!file) return;

      // Max size: 5MB
      if (file.size > 5 * 1024 * 1024) {
        preview.innerHTML = `<p class="text-danger small mt-1">❌ File too large (max 5MB)</p>`;
        input.value = "";
        return;
      }

      const ext = file.name.split(".").pop().toLowerCase();
      const validExts = imageOnly
        ? ["jpg", "jpeg", "png"]
        : ["jpg", "jpeg", "png", "pdf", "docx", "doc"];
      if (!validExts.includes(ext)) {
        preview.innerHTML = `<p class="text-danger small mt-1">❌ Invalid file type. Allowed: ${validExts.join(", ")}</p>`;
        input.value = "";
        return;
      }

      // Display preview
      if (["jpg", "jpeg", "png"].includes(ext)) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = "200px";
        img.classList.add("img-thumbnail", "mt-2");
        preview.appendChild(img);
      } else {
        preview.innerHTML = `<p class="small mt-2 text-muted">📄 ${file.name}</p>`;
      }
    });
  };

  // Setup file previews
  handlePreview("id_logo", "logo_preview", true);
  handlePreview("id_proposal_file", "proposal_preview");
  handlePreview("id_company_profile", "profile_preview");
  handlePreview("id_tax_compliance_certificate", "tax_preview");

  // ----------------------------
  // ✅ Client-side validation
  // ----------------------------
  const validateForm = () => {
    let valid = true;
    let firstInvalid = null;

    const requiredFields = [
      "id_organization_name",
      "id_sector",
      "id_contact_full_name",
      "id_contact_email",
      "id_contact_phone",
    ];

    // Helper to attach/remove validation message
    const setInvalid = (el, message) => {
      el.classList.add("is-invalid");
      if (!el.nextElementSibling || !el.nextElementSibling.classList.contains("invalid-feedback")) {
        const msg = document.createElement("div");
        msg.className = "invalid-feedback";
        msg.textContent = message;
        el.insertAdjacentElement("afterend", msg);
      } else {
        el.nextElementSibling.textContent = message;
      }
      if (!firstInvalid) firstInvalid = el;
      valid = false;
    };

    const clearInvalid = (el) => {
      el.classList.remove("is-invalid");
      if (el.nextElementSibling && el.nextElementSibling.classList.contains("invalid-feedback")) {
        el.nextElementSibling.remove();
      }
    };

    // Required checks
    requiredFields.forEach((id) => {
      const el = document.getElementById(id);
      if (el && !el.value.trim()) {
        setInvalid(el, "This field is required.");
      } else if (el) {
        clearInvalid(el);
      }
    });

    // Email validation
    const emailEl = document.getElementById("id_contact_email");
    if (emailEl && emailEl.value.trim()) {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailPattern.test(emailEl.value.trim())) {
        setInvalid(emailEl, "Please enter a valid email address.");
      }
    }

    // Phone validation (basic)
    const phoneEl = document.getElementById("id_contact_phone");
    if (phoneEl && phoneEl.value.trim()) {
      const phonePattern = /^[\d\s+\-()]{7,15}$/;
      if (!phonePattern.test(phoneEl.value.trim())) {
        setInvalid(phoneEl, "Enter a valid phone number.");
      }
    }

    // Website validation
    const websiteEl = document.getElementById("id_website");
    if (websiteEl && websiteEl.value.trim()) {
      try {
        new URL(websiteEl.value.trim());
        clearInvalid(websiteEl);
      } catch {
        setInvalid(websiteEl, "Please enter a valid website URL (e.g., https://example.com)");
      }
    }

    // Consent checkbox
    const consent = document.getElementById("id_consent_confirmation");
    if (consent && !consent.checked) {
      consent.classList.add("is-invalid");
      valid = false;
      if (!firstInvalid) firstInvalid = consent;
    } else if (consent) {
      consent.classList.remove("is-invalid");
    }

    // Scroll to first invalid
    if (!valid && firstInvalid) {
      firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
      firstInvalid.focus();
    }

    return valid;
  };

  // ----------------------------
  // 🚀 AJAX form submission
  // ----------------------------
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!validateForm()) {
      showAlert("Please correct the highlighted errors.", "danger");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting...`;

    const formData = new FormData(form);

    fetch(form.action || window.location.href, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: formData,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Network response not ok");
        return res.json().catch(() => ({}));
      })
      .then((data) => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Sponsorship Application`;

        if (data.success) {
          showAlert(data.message || "Sponsorship application submitted successfully!", "success");
          form.reset();
          ["logo_preview", "proposal_preview", "profile_preview", "tax_preview"].forEach((id) => {
            const preview = document.getElementById(id);
            if (preview) preview.innerHTML = "";
          });
          form.querySelectorAll(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
        } else if (data.errors) {
          Object.entries(data.errors).forEach(([field, messages]) => {
            const el = document.getElementById(`id_${field}`);
            if (el) {
              el.classList.add("is-invalid");
              const err = document.createElement("div");
              err.className = "invalid-feedback";
              err.textContent = messages.join(", ");
              el.insertAdjacentElement("afterend", err);
            }
          });
          showAlert("Please correct the highlighted errors.", "danger");
        } else {
          showAlert("Something went wrong. Please try again.", "danger");
        }
      })
      .catch((err) => {
        console.error("AJAX Error:", err);
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Sponsorship Application`;
        showAlert("Server error. Please try again later.", "danger");
      });
  });
});


// Set footer year if needed
document.getElementById("year").textContent = new Date().getFullYear();



// Translater
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.querySelector('.translate-toggle');
  const popover = document.querySelector('.translate-popover');

  if (toggleBtn && popover) {
    // Toggle on click
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation(); // don’t trigger document click
      popover.classList.toggle('d-none');
    });

    // Hide when clicking outside
    document.addEventListener('click', (e) => {
      if (!popover.contains(e.target) && !toggleBtn.contains(e.target)) {
        popover.classList.add('d-none');
      }
    });
  }
});


// Translate popover toggle for mobile globe icon
document.querySelectorAll('.translate-toggle').forEach(function(globe) {
  globe.addEventListener('click', function(e) {
    // Only for mobile globe icon (d-xl-none)
    if (this.classList.contains('d-xl-none')) {
      e.stopPropagation();
      const popover = document.querySelector('.translate-popover');
      if (popover) {
        popover.classList.toggle('d-none');
      }
    }
  });
});
// Hide popover when clicking outside
document.addEventListener('click', function(e) {
  const popover = document.querySelector('.translate-popover');
  if (popover && !popover.classList.contains('d-none')) {
    // If click is outside popover and globe
    if (!e.target.closest('.translate-popover') && !e.target.closest('.translate-toggle')) {
      popover.classList.add('d-none');
    }
  }
});


// modal
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("bioModal");
  const closeBtn = document.querySelector(".bio-close");

  document.querySelectorAll(".profile-btn").forEach(btn => {
    btn.addEventListener("click", function(e) {
      e.preventDefault();
      document.getElementById("bioName").textContent = this.dataset.name;
      document.getElementById("bioPosition").textContent = this.dataset.position;
      document.getElementById("bioOrg").textContent = this.dataset.org;
      document.getElementById("bioPhoto").src = this.dataset.photo;
      document.getElementById("bioText").textContent = this.dataset.bio;
      modal.style.display = "flex";
    });
  });

  // Close modal
  closeBtn.addEventListener("click", () => modal.style.display = "none");
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });
});


document.addEventListener("DOMContentLoaded", function() {
    const hash = window.location.hash;
    if (hash) {
        const target = document.querySelector(hash);
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    }
});
