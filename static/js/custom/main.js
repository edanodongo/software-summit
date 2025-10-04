
// Minimal dark theme CSS
const darkStyle = document.createElement('style');
darkStyle.textContent = `
body.dark-theme {
background: #181818 !important;
color: #f1f1f1 !important;
}
body.dark-theme .navbar, body.dark-theme .navbar * {
background: #232323 !important;
color: #fff !important;
}
body.dark-theme .card, body.dark-theme .section-padding, body.dark-theme .bg-light, body.dark-theme .agenda-day, body.dark-theme .feature-card, body.dark-theme .objective-card {
background: #232323 !important;
color: #f1f1f1 !important;
}
body.dark-theme .card-header, body.dark-theme .card-body {
background: #232323 !important;
color: #f1f1f1 !important;
}
body.dark-theme .btn-outline-light, body.dark-theme .btn-outline-custom {
border-color: #fff !important;
color: #fff !important;
}
body.dark-theme .btn-outline-light:hover, body.dark-theme .btn-outline-custom:hover {
background: #fff !important;
color: #232323 !important;
}
body.dark-theme .footer, body.dark-theme .footer * {
background: #181818 !important;
color: #f1f1f1 !important;
}
body.dark-theme .media-item, body.dark-theme .media-overlay {
background: #232323 !important;
color: #f1f1f1 !important;
}
body.dark-theme .form-control, body.dark-theme .form-select {
background: #232323 !important;
color: #f1f1f1 !important;
border-color: #444 !important;
}
body.dark-theme .agenda-item {
background: #232323 !important;
color: #f1f1f1 !important;
}
body.dark-theme .bg-white, body.dark-theme .bg-light {
background: #232323 !important;
color: #f1f1f1 !important;
}
body.dark-theme .alert-info {
background: #232323 !important;
color: #f1f1f1 !important;
border-color: #444 !important;
}
body.dark-theme .partner-logo {
filter: grayscale(100%) brightness(0.8) invert(1);
}
`;
document.head.appendChild(darkStyle);



// Initialize AOS (Animate On Scroll)
AOS.init({
    duration: 1000,
    easing: 'ease-in-out',
    once: true,
    offset: 100
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 80;
            const elementPosition = target.offsetTop;
            const offsetPosition = elementPosition - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Navbar background change on scroll
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    const scrollTop = window.pageYOffset;

    if (scrollTop > 50) {
        navbar.style.background = 'rgba(28, 28, 24, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.2)';
    } else {
        navbar.style.background = 'rgba(28, 28, 24, 0.95)';
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
    }
});

// Scroll to top functionality
const scrollToTopBtn = document.getElementById('scrollToTop');

window.addEventListener('scroll', function () {
    if (window.pageYOffset > 300) {
        scrollToTopBtn.classList.add('show');
    } else {
        scrollToTopBtn.classList.remove('show');
    }
});

scrollToTopBtn.addEventListener('click', function () {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

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


});

// Set footer year if needed
document.getElementById("year").textContent = new Date().getFullYear();







// Registration pricing animation
document.querySelectorAll('.pricing-card-title').forEach(priceElement => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'pulse 2s infinite';
            }
        });
    });

    observer.observe(priceElement);
});

// Partner logo hover effects
// document.querySelectorAll('.partner-logo').forEach(logo => {
//     logo.addEventListener('mouseenter', function () {
//         this.style.transform = 'scale(1.1) rotate(5deg)';
//     });

//     logo.addEventListener('mouseleave', function () {
//         this.style.transform = 'scale(1) rotate(0deg)';
//     });
// });

// Typing effect for hero title
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

// Initialize typing effect when page loads
window.addEventListener('load', function () {
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const originalText = heroTitle.textContent;
        typeWriter(heroTitle, originalText, 100);
    }
});

// Countdown timer (if event is in future)
function updateCountdown() {
    const eventDate = new Date('2025-10-28T00:00:00').getTime();
    const now = new Date().getTime();
    const timeLeft = eventDate - now;

    if (timeLeft > 0) {
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

        // Update all countdown displays
        const countdownElements = [
            document.getElementById('countdown'),
            document.getElementById('countdown-agenda')
        ];
        countdownElements.forEach(countdownElement => {
            if (countdownElement) {
                countdownElement.innerHTML = `
                <div class="countdown-item">
                    <span class="countdown-number">${days}</span>
                    <span class="countdown-label">Days</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number">${hours}</span>
                    <span class="countdown-label">Hours</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number">${minutes}</span>
                    <span class="countdown-label">Minutes</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number">${seconds}</span>
                    <span class="countdown-label">Seconds</span>
                </div>
            `;
            }
        });
    }
}

// Update countdown every second
setInterval(updateCountdown, 1000);
updateCountdown(); // Initial call

// Add CSS animations for various elements
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fadeInScale {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    .countdown-item {
        display: inline-block;
        text-align: center;
        margin: 0 15px;
    }
    
    .countdown-number {
        display: block;
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    
    .countdown-label {
        display: block;
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        text-transform: uppercase;
    }
`;
document.head.appendChild(style);

console.log('Kenya Software Summit 2025 - Website loaded successfully!');
console.log('Code the Future. Build Africa. 🇰🇪');


// Initialize AOS
AOS.init({
    duration: 800,
    once: true,
    offset: 100
});

// Add smooth scrolling and enhanced interactions
document.addEventListener('DOMContentLoaded', function () {
    // Add hover effects to agenda items
    const agendaItems = document.querySelectorAll('.agenda-item');
    agendaItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-4px)';
        });

        item.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    // Tab switching animation
    const tabButtons = document.querySelectorAll('[data-bs-toggle="pill"]');
    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Add loading animation or transition effects here
            setTimeout(() => {
                AOS.refresh();
            }, 100);
        });
    });
});







