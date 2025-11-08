const toggleBtn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");
    const topbar = document.getElementById("topbar");
    const content = document.getElementById("content");
    const footer = document.getElementById("footer");
    const overlay = document.getElementById("overlay");

    toggleBtn.addEventListener("click", () => {
        if (window.innerWidth <= 992) {
            sidebar.classList.toggle("active");
            overlay.classList.toggle("active");
        } else {
            sidebar.classList.toggle("collapsed");
            topbar.classList.toggle("shifted");
            content.classList.toggle("shifted");
            footer.classList.toggle("shifted");
        }
    });

    overlay.addEventListener("click", () => {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    });