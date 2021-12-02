from flask import Flask, redirect, url_for, render_template, abort
import time
import json
import requests
import base64

def get_user_and_token(filename):
    with open(filename) as file:
        conf = json.load(file)
        user = conf['user']
        token = conf['token']
        return user, token

def get_subdomain(filename):
    with open(filename) as file:
        conf = json.load(file)
        subdomain = conf['subdomain']
        return subdomain

def get_base64_string(user, token):
    auth_str = user + '/token:' + token
    auth_bytes = auth_str.encode('ascii')
    auth_enc_str = base64.b64encode(auth_bytes).decode('ascii')

    return auth_enc_str

def make_headers(filename):
    user, token = get_user_and_token(filename)
    auth_enc_str = get_base64_string(user, token)
    headers = { 'Authorization': 'Basic ' + auth_enc_str }
    return headers

def init_paginate(filename):
    subdomain = get_subdomain(filename)
    url = 'https://' + subdomain + '.zendesk.com/api/v2/tickets.json?page[size]=25'
    pages = [url]

    headers = make_headers('config.json')
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        while data['meta']['has_more'] == True:
            pages.append(data['links']['next'])
            r = requests.get(data['links']['next'], headers=headers)
            data = r.json()
        return pages

def update_paginate(filename, pages):
    subdomain = get_subdomain(filename)
    url = pages[len(pages) - 1]
    headers = make_headers('config.json')
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        while data['meta']['has_more'] == True:
            pages.append(data['links']['next'])
            r = requests.get(data['links']['next'], headers=headers)
            data = r.json()

page_list = init_paginate('config.json')

app = Flask(__name__)

@app.route('/')
def index():
    headers = make_headers('config.json')
    subdomain = get_subdomain('config.json')
    endpoint = 'https://' + subdomain + '.zendesk.com/api/v2/tickets.json?page[size]=25'
    r = requests.get(endpoint, headers=headers)
    if r.status_code == 200:
        update_paginate('config.json', page_list)
        data = r.json()
        return render_template('index.html', tickets=data['tickets'], endpoint=endpoint, pages=page_list)
    elif r.status_code == 401:
        return redirect(url_for('error_401'))

@app.route('/<int:page>')
def pages(page):
    if page == 0:
        return redirect(url_for('index'))
    headers = make_headers('config.json')
    update_paginate('config.json', page_list)
    if page < 0 or page >= len(page_list):
       abort(404)
    else:
        endpoint = page_list[page]
        r = requests.get(endpoint, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return render_template('index.html', tickets=data['tickets'], endpoint=endpoint, pages=page_list)
        elif r.status_code == 401:
            return redirect(url_for('error_401'))

@app.route('/ticket/<int:ticket_id>')
def ticket(ticket_id):
    headers = make_headers('config.json')
    subdomain = get_subdomain('config.json')
    endpoint = 'https://' + subdomain + '.zendesk.com/api/v2/tickets/' + str(ticket_id)
    r = requests.get(endpoint, headers=headers)
    if r.status_code == 200:
        data = r.json()
        return render_template('ticket.html', ticket=data['ticket'])
    else:
        if r.status_code == 401:
            return redirect(url_for('error_401'))
        elif r.status_code == 404:
            abort(404)    

@app.route('/unauthorized')
def error_401():
    headers = make_headers('config.json')
    subdomain = get_subdomain('config.json')
    endpoint = 'https://' + subdomain + '.zendesk.com/api/v2/tickets'
    r = requests.get(endpoint, headers=headers)
    if r.status_code == 200:
        return redirect(url_for('index'))
    else:
        return render_template('unauthorized.html')

@app.errorhandler(404)
def error_404(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def error_500(e):
    return render_template('errors/500.html'), 500
