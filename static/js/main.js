/**
 * Template Name: Evently
 * Template URL: https://bootstrapmade.com/evently-bootstrap-events-template/
 * Updated: Jul 19 2025 with Bootstrap v5.3.7
 * Author: BootstrapMade.com
 * License: https://bootstrapmade.com/license/
 */

(function () {
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
        navmenu.addEventListener('click', function (e) {
            e.preventDefault();
            this.parentNode.classList.toggle('active');
            this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
            e.stopImmediatePropagation();
        });
    });

/**
 * Preloader + Theme Handler
 */
(function() {
    const preloader = document.getElementById("preloader");
    const content = document.getElementById("content");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

    // --- Instant Theme Application (runs immediately, before DOMContentLoaded)
    const savedTheme = localStorage.getItem("theme");
    const initialTheme = savedTheme || (prefersDark.matches ? "dark-mode" : "light-mode");
    document.documentElement.classList.add("js-enabled"); // optional helper
    document.body.classList.add(initialTheme);

    // Wait for DOM to attach buttons and listeners
    document.addEventListener("DOMContentLoaded", () => {

        // --- Apply Theme Function
        function applyTheme(theme) {
            document.body.classList.remove("light-mode", "dark-mode");
            document.body.classList.add(theme);
            localStorage.setItem("theme", theme);
        }

        // --- System theme change
        prefersDark.addEventListener("change", (e) => {
            if (!localStorage.getItem("theme")) {
                applyTheme(e.matches ? "dark-mode" : "light-mode");
            }
        });

        // --- Manual toggle
        const toggleBtn = document.getElementById("theme-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                applyTheme(document.body.classList.contains("dark-mode")
                    ? "light-mode"
                    : "dark-mode"
                );
            });
        }

        // --- Preloader fade out after full load
        window.addEventListener("load", () => {
            // Give a small delay for transition smoothness
            setTimeout(() => {
                if (preloader) preloader.classList.add("fade-out");
                if (content) content.style.display = "block";
            }, 400); // reduced delay for smoother experience
        });
    });
})();



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

    document.querySelectorAll('.countdown').forEach(function (countDownItem) {
        updateCountDown(countDownItem);
        setInterval(function () {
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
        document.querySelectorAll(".init-swiper").forEach(function (swiperElement) {
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

    pricingContainers.forEach(function (container) {
        const pricingSwitch = container.querySelector('.pricing-toggle input[type="checkbox"]');
        const monthlyText = container.querySelector('.monthly');
        const yearlyText = container.querySelector('.yearly');

        pricingSwitch.addEventListener('change', function () {
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
    // =====================================================
    // 🔹 ELEMENT REFERENCES
    // =====================================================
    const form = document.getElementById("registration-form");
    const submitBtn = document.getElementById("submit-btn");
    const alertContainer = document.getElementById("alert-container");

    const otherInterestWrapper = document.getElementById("other-interest");
    const interestCheckboxes = document.querySelectorAll("#id_interests input[type=checkbox]");
    const otherInterestInput = document.getElementById("id_other_interest");

    // =====================================================
    // 🔹 CSRF TOKEN HELPER
    // =====================================================
    const getCookie = (name) => {
        const cookies = document.cookie ? document.cookie.split(";") : [];
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    };
    const csrftoken = getCookie("csrftoken");

    // =====================================================
    // 🔹 UTILITIES
    // =====================================================
    const toggleVisibility = (wrapper, input, show) => {
        if (!wrapper || !input) return;
        wrapper.style.display = show ? "block" : "none";
        show ? input.setAttribute("required", "required") : input.removeAttribute("required");
        if (!show) input.value = "";
    };

    const showAlert = (message, type = "success") => {
        alertContainer.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="autoDismissAlert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
        setTimeout(() => {
            const alertBox = document.getElementById("autoDismissAlert");
            if (alertBox) {
                alertBox.classList.remove("show");
                alertBox.classList.add("fade");
                setTimeout(() => alertBox.remove(), 500);
            }
        }, 8000);
    };

    // =====================================================
    // 🔹 INTEREST FIELD TOGGLE
    // =====================================================
    const handleInterestChange = () => {
        const othersChecked = Array.from(interestCheckboxes).some(
            (cb) => cb.checked && cb.value.toLowerCase() === "others"
        );
        toggleVisibility(otherInterestWrapper, otherInterestInput, othersChecked);
    };

    interestCheckboxes.forEach((cb) => cb.addEventListener("change", handleInterestChange));
    handleInterestChange();

    // =====================================================
    // 🔹 AJAX FORM SUBMISSION
    // =====================================================
    form?.addEventListener("submit", (e) => {
        e.preventDefault();

        // Clear previous errors
        form.querySelectorAll(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
        form.querySelectorAll(".invalid-feedback").forEach((el) => el.remove());
        alertContainer.innerHTML = "";

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting...`;

        const formData = new FormData(form);

        // ✅ Ensure interests are sent as multiple values
        formData.delete("interests");
        interestCheckboxes.forEach((cb) => {
            if (cb.checked) formData.append("interests", cb.value);
        });

        // ✅ Ensure privacy checkbox sends proper boolean
        const privacyCb = form.querySelector("[name='privacy_agreed']");
        if (privacyCb) {
            formData.delete("privacy_agreed");
            if (privacyCb.checked) formData.append("privacy_agreed", "true");
        }

        // ✅ Ensure updates_opt_in sends correct value
        const updatesCb = form.querySelector("[name='updates_opt_in']");
        if (updatesCb) {
            formData.delete("updates_opt_in");
            if (updatesCb.checked) formData.append("updates_opt_in", "true");
        }

        // =====================================================
        // 🔹 AJAX SUBMIT
        // =====================================================
        fetch(form.action || window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken,
            },
        })
            .then((res) => res.json())
            .then((data) => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Registration`;

                console.log("🧩 Server response:", data);

                if (data.success) {
                    showAlert(data.message || "Registration successful!", "success");
                    form.reset();
                    handleInterestChange();

                    // Clear previews
                    ["id_national_id_scan", "id_passport_photo"].forEach((id) => {
                        const input = document.getElementById(id);
                        const preview = document.getElementById(
                            id === "id_national_id_scan" ? "id_scan_preview" : "passport_preview"
                        );
                        if (input) input.value = "";
                        if (preview) preview.innerHTML = "";
                    });

                } else if (data.errors) {
                    let globalErrors = [];
                    let firstInvalidEl = null;

                    Object.entries(data.errors).forEach(([field, errors]) => {
                        const inputEl = form.querySelector(`#id_${field}`);

                        if (inputEl) {
                            inputEl.classList.add("is-invalid");
                            const errorDiv = document.createElement("div");
                            errorDiv.className = "invalid-feedback";
                            errorDiv.innerText = errors.join(", ");
                            if (!inputEl.nextElementSibling?.classList.contains("invalid-feedback")) {
                                inputEl.insertAdjacentElement("afterend", errorDiv);
                            }
                            if (!firstInvalidEl) firstInvalidEl = inputEl;
                        } else {
                            // If no matching field (e.g. general or choice errors like days_to_attend)
                            globalErrors.push(errors.join(", "));
                        }
                    });

                    if (globalErrors.length > 0) {
                        showAlert(globalErrors.join("<br>"), "danger");
                    }

                    if (firstInvalidEl) {
                        firstInvalidEl.scrollIntoView({ behavior: "smooth", block: "center" });
                        firstInvalidEl.focus();
                    }

                } else if (data.message) {
                    showAlert(data.message, "warning");
                } else {
                    showAlert("Something went wrong. Please try again.", "danger");
                }
            })
            .catch((err) => {
                console.error("❌ AJAX error:", err);
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Registration`;
                showAlert("Server error. Please try again later.", "danger");
            });
    });

    // =====================================================
    // 🔹 FILE PREVIEW HANDLER
    // =====================================================
    const handlePreview = (inputId, previewId, isImageOnly = true) => {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        if (!input || !preview) return;

        input.addEventListener("change", function () {
            preview.innerHTML = "";
            const file = this.files[0];
            if (!file) return;

            if (file.size > 2 * 1024 * 1024) {
                preview.innerHTML = `<p class="text-danger">❌ File too large. Max size is 2MB.</p>`;
                this.value = "";
                return;
            }

            const ext = file.name.split(".").pop().toLowerCase();
            const validExts = isImageOnly ? ["jpg", "jpeg", "png"] : ["jpg", "jpeg", "png", "pdf"];

            if (!validExts.includes(ext)) {
                preview.innerHTML = `<p class="text-danger">❌ Invalid file type. Allowed: ${validExts.join(", ")}</p>`;
                this.value = "";
                return;
            }

            const container = document.createElement("div");
            container.classList.add("d-flex", "align-items-center", "gap-3", "mt-2");

            if (ext === "pdf") {
                container.innerHTML = `<span>📄 <strong>${file.name}</strong> uploaded successfully.</span>`;
            } else {
                const img = document.createElement("img");
                img.src = URL.createObjectURL(file);
                img.classList.add("img-thumbnail");
                img.style.maxWidth = "200px";
                img.style.height = "auto";
                container.appendChild(img);
            }

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "btn btn-sm btn-outline-danger";
            removeBtn.textContent = "Remove file";
            removeBtn.addEventListener("click", () => {
                input.value = "";
                preview.innerHTML = "";
            });
            container.appendChild(removeBtn);

            preview.appendChild(container);
            preview.insertAdjacentHTML(
                "beforeend",
                `<p class="small text-muted mt-1">✅ ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</p>`
            );
        });
    };

    // =====================================================
    // 🔹 INIT FILE PREVIEWS
    // =====================================================
    handlePreview("id_national_id_scan", "id_scan_preview", false);
    handlePreview("id_passport_photo", "passport_preview", true);
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
document.querySelectorAll('.translate-toggle').forEach(function (globe) {
    globe.addEventListener('click', function (e) {
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
document.addEventListener('click', function (e) {
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
        btn.addEventListener("click", function (e) {
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


document.addEventListener('DOMContentLoaded', () => {
  const dropdowns = document.querySelectorAll('.drop-auto');
  dropdowns.forEach(drop => {
    const toggle = drop.querySelector('[data-bs-toggle="dropdown"]');
    const menu = drop.querySelector('.dropdown-menu');

    toggle.addEventListener('show.bs.dropdown', () => {
      const rect = toggle.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;

      // If not enough space below, open upward
      if (spaceBelow < 200 && spaceAbove > spaceBelow) {
        drop.classList.add('dropup');
      } else {
        drop.classList.remove('dropup');
      }
    });
  });
});