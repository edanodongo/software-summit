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
  const preloader = document.querySelector('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove();
    });
  }

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



// Form submission with AJAX
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registration-form");
  const submitBtn = document.getElementById("submit-btn");
  const alertContainer = document.getElementById("alert-container");

  // --- Get wrapper divs ---
  const otherOrgWrapper = document.getElementById("other-org-type");
  const otherInterestWrapper = document.getElementById("other-interest");

  // --- Get form elements ---
  const orgTypeSelect = document.getElementById("id_organization_type");
  const otherOrgInput = document.getElementById("id_other_organization_type");

  const interestCheckboxes = document.querySelectorAll(
    "#id_interests input[type=checkbox]"
  );
  const otherInterestInput = document.getElementById("id_other_interest");

  // --- Utility to toggle visibility ---
  function toggleVisibility(wrapper, input, show) {
    if (!wrapper || !input) return;
    if (show) {
      wrapper.style.display = "block";
      input.setAttribute("required", "required");
    } else {
      wrapper.style.display = "none";
      input.removeAttribute("required");
      input.value = ""; // clear hidden field
    }
  }

  // --- Handle Organization Type ---
  function handleOrgTypeChange() {
    if (orgTypeSelect && orgTypeSelect.value) {
      toggleVisibility(otherOrgWrapper, otherOrgInput, true);
    } else {
      toggleVisibility(otherOrgWrapper, otherOrgInput, false);
    }
  }

  // --- Handle Interests ---
  function handleInterestChange() {
    let othersChecked = Array.from(interestCheckboxes).some(
      (cb) => cb.checked && cb.value.toLowerCase() === "others"
    );
    toggleVisibility(otherInterestWrapper, otherInterestInput, othersChecked);
  }

  // --- Event listeners ---
  if (orgTypeSelect) {
    orgTypeSelect.addEventListener("change", handleOrgTypeChange);
  }
  interestCheckboxes.forEach((cb) =>
    cb.addEventListener("change", handleInterestChange)
  );

  // --- Run on page load (restore state if editing form) ---
  handleOrgTypeChange();
  handleInterestChange();

  // --- Alerts ---
  function showAlert(message, type = "success") {
    alertContainer.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
  }

  // --- AJAX Form Submit ---
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting...`;

    fetch(form.action || window.location.href, {
      method: "POST",
      body: new FormData(form),
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Registration`;

        if (data.success) {
          showAlert(data.message, "success");
          form.reset();
          handleOrgTypeChange();
          handleInterestChange();
        } else if (data.errors) {
          let errorList = Object.entries(data.errors)
            .map(
              ([field, errors]) =>
                `<li><strong>${field}:</strong> ${errors.join(", ")}</li>`
            )
            .join("");
          showAlert(`<ul>${errorList}</ul>`, "danger");
        } else {
          showAlert("Something went wrong. Please try again.", "danger");
        }
      })
      .catch((err) => {
        console.error("Error:", err);
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa fa-paper-plane me-2"></i> Submit Registration`;
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