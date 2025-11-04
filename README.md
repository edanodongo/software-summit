<p align="center">

  ![Summit Logo](static/images/summit_logo_dark.png#gh-dark-mode-only)
  ![Summit Logo](repo/images/summit_logo_light.png.png#gh-light-mode-only)

</p>

---

<div align="center">
  [![](https://img.shields.io/github/issues/edanodongo/software-summit?style=for-the-badge)](https://github.com/edanodongo/software-summit/issues)
  <!-- [![](https://img.shields.io/github/license/edanodongo/software-summit?style=for-the-badge)](https://github/nfoert/cardie/blob/main/LICENSE) -->


  **The latest changes are available in the [main](https://github.com/edanodongo/software-summit/tree/main) branch! Please check there for the most up to date changes.**

</div>


Design a unlimited number of business or information cards about yourself, share a link or QR code to them, print it out, and save other people's cards to your virtual wallet for later. Once you've created a card you can get analytics data on how your cards are getting visited, you can edit your cards as things change, and you can keep cards private so only people with a link to your card can see it.

> [!IMPORTANT]
> This Project is developed using the tools/languages below.

<div align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=django,python,html,css,js,github,git,alpinejs"/>
  </a>
</div>


## Installation

First, clone this repository using the following command
```bash
git clone https://github.com/edanodongo/software-summit.git
```

Then, navigate to that directory and create a new python virtual environment
```bash
cd software-summit
python3 -m venv .venv
```

Activate the virtual environment using the command for your system (Linux is used here) and install the required dependencies
```bash
source ./.venv/bin/activate
pip install -r requirements.txt
```

create your config.json RESEMBLING a .env


Next, make and migrate the models
```bash
python manage.py makemigrations
python manage.py migrate
```

Now just run the server using the following command, or run the `Start server` task in your Visual Studio Code
```bash
python manage.py runserver
```
