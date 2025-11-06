<p align="center">

  ![Summit Logo](https://github.com/edanodongo/software-summit/blob/main/static/images/summit_logo.png#gh-dark-mode-only)
  ![Summit Logo](https://github.com/edanodongo/software-summit/blob/main/static/images/summit_logo.png#gh-light-mode-only)

</p>

---

<div align="center">

  **The latest changes are available in the [main](https://github.com/edanodongo/software-summit/tree/main) branch!**
</div>


---

## 🧩 Overview

The **Software Summit Portal** is a web application developed for the **Kenya Software Summit 2025**.  
It provides a centralized system to:

- 🧾 **Register participants** and manage attendee information 
- 🧾 **Register Exhibitors and Sponsors**
- 👤 **Manage user accounts** for both applicants and administrators  
- 🪪 **Generate and print summit badges** dynamically (with color-coded categories)  
- ℹ️ **Share event details** and updates about the summit  

The system also logs all badge printing activities for audit and supports reprints when needed.

🌐 <a href="https://softwaresummit.go.ke" target="_blank" rel="noopener noreferrer">Official Website</a>  

---

> [!IMPORTANT]
> This project is developed using the tools and languages below.

<div align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=django,python,html,css,js,bootstrap,git,github" />
  </a>
</div>


## Installation

First, clone this repository using the following command
```bash
git clone https://github.com/edanodongo/software-summit.git
```

Then, navigate to that directory and create a new python virtual environment(macOS/Linux)
```bash
cd software-summit
python3 -m venv venv
```
Then, navigate to that directory and create a new python virtual environment(Windows)
```bash
cd software-summit
python -m venv venv
```

Activate the virtual environment using the command for your system (macOS/Linux) and install the required dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```
Activate the virtual environment using the command for your system (for windows) and install the required dependencies
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

create your config.json RESEMBLING a .env


Next, make and migrate the models
```bash
python manage.py makemigrations
python manage.py migrate
```

Now just run the server using the following command, or run the `Start server` task in your Editor/IDE
```bash
python manage.py runserver
```
