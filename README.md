# Zendesk Ticket Viewer

### *A Flask web app for viewing Zendesk tickets*

---

## Installation

1. Download repo
2. Edit the `config.json` file in the top-level directory and replace the values with your email, API token and Zendesk subdomain:
```
{
    "user": "<YOUR_EMAIL_HERE>",
    "token": "<YOUR_API_TOKEN_HERE>",
    "subdomain": "<YOUR_ZENDESK_SUBDOMAIN_HERE>"
}
```
2. Create Python virtual environment in top-level directory: `python -m venv venv`
3. Activate the virtual environment
    - Windows: `venv\Scripts\activate`
    - Mac: `venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Finally, start the server: `flask run`

You should be able to see the web app on `127.0.0.1:5000` once the command line output reads `"Running on..."`

---

## Usage
- Click on the page title "Zendesk Ticket Viewer" to go back to the home page
- Use the "Previous Page" and "Next Page" to flip between pages
- Cick on the ticket title to view the detailed single ticket info