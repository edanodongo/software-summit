document.getElementById('mailForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("{% url 'auth_send_mail' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            notyf.success(data.message);
            document.getElementById('mailForm').reset();
        } else {
            notyf.error(data.message);
        }
    })
    .catch(() => {
        notyf.error('Something went wrong. Try again later.');
    });
});

