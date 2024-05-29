from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, SkincareFormEntry
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import requests

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/skincare-form', methods=['GET', 'POST'])
def skincare_form():
    if request.method == 'POST':
        # Process form submission
        cleanser = request.form.get('cleanser')
        toner = request.form.get('toner')
        moisturizer = request.form.get('moisturizer')
        serum = request.form.get('serum')
        sunscreen = request.form.get('sunscreen')

        new_entry = SkincareFormEntry(
            cleanser=cleanser,
            toner=toner,
            moisturizer=moisturizer,
            serum=serum,
            sunscreen=sunscreen

        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Skincare form submitted successfully!', category='success')

        # Redirect to GET request to prevent form resubmission on page refresh
        return redirect(url_for('auth.skincare_form'))

    # Handle GET request to display existing entries
    entries = SkincareFormEntry.query.all()
    return render_template("skincare_form.html", user=current_user, entries=entries)


@auth.route('/delete-entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = SkincareFormEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', category='success')
    return redirect(url_for('auth.skincare_form'))


@auth.route('/sort-entries', methods=['POST'])
def sort_entries():
    data = request.json
    sort_key = data.get('sort_key')
    sort_order = data.get('sort_order', 'asc')

    # Fetch the entries from the database without sorting
    entries = SkincareFormEntry.query.all()

    # Prepare the entries list with delete_url included
    entries_list = [{
        'id': entry.id,
        'cleanser': entry.cleanser,
        'toner': entry.toner,
        'moisturizer': entry.moisturizer,
        'serum': entry.serum,
        'sunscreen': entry.sunscreen,
        'delete_url': url_for('auth.delete_entry', entry_id=entry.id)  # Ensure correct blueprint reference
    } for entry in entries]

    # Send the data to the microservice for sorting
    response = requests.post('http://localhost:5001/sort', json={
        'entries': entries_list,
        'sort_key': sort_key,
        'sort_order': sort_order
    })

    # Check if the response from the microservice was successful
    if response.status_code == 200:
        sorted_entries = response.json()
    else:
        sorted_entries = entries_list  # Fallback to unsorted entries in case of an error

    return jsonify(sorted_entries)
