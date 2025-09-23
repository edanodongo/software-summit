const emailInput = document.getElementById('emailInput');
  const feedback = document.getElementById('emailFeedback');
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  emailInput.addEventListener('input', function () {
    const email = emailInput.value;

    if (!email) {
      feedback.textContent = '';
      feedback.className = 'form-text';
    } else if (emailRegex.test(email)) {
      feedback.textContent = 'Looks good!';
      feedback.className = 'form-text text-success';
    } else {
      feedback.textContent = 'Please enter a valid email like name@example.com';
      feedback.className = 'form-text text-danger';
    }
  });