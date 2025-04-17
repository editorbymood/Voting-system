import os
import logging
from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, Candidate, Vote
from forms import RegistrationForm, LoginForm, CandidateForm, VoteForm
from utils import admin_required
from urllib.parse import urlparse
from datetime import datetime
from email_service import send_registration_confirmation, send_login_notification, send_candidate_notification, EMAIL_ENABLED

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add 'now' to all template contexts
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Send registration confirmation email
        if EMAIL_ENABLED:
            try:
                send_registration_confirmation(user.username, user.email)
                logger.info(f"Registration email sent to {user.email}")
                flash('Your account has been created! A confirmation email has been sent to your address.', 'success')
            except Exception as e:
                logger.error(f"Failed to send registration email: {str(e)}")
                flash('Your account has been created! You can now log in.', 'success')
        else:
            logger.info(f"Email notifications disabled. Skipping registration email to {user.email}")
            flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('voter_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember.data)
        
        # Send login notification email
        if EMAIL_ENABLED:
            try:
                send_login_notification(user.username, user.email)
                logger.info(f"Login notification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send login notification email: {str(e)}")
        else:
            logger.info(f"Email notifications disabled. Skipping login notification to {user.email}")
            
        next_page = request.args.get('next')
        
        if not next_page or urlparse(next_page).netloc != '':
            if user.role == 'admin':
                next_page = url_for('admin_dashboard')
            else:
                next_page = url_for('voter_dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_voters = User.query.filter_by(role='voter').count()
    total_candidates = Candidate.query.count()
    total_votes = Vote.query.count()
    recent_votes = Vote.query.order_by(Vote.timestamp.desc()).limit(5).all()
    
    stats = {
        'total_voters': total_voters,
        'total_candidates': total_candidates,
        'total_votes': total_votes,
        'voted_percentage': (total_votes / total_voters * 100) if total_voters > 0 else 0
    }
    
    return render_template('admin/dashboard.html', title='Admin Dashboard', stats=stats, recent_votes=recent_votes)

@app.route('/admin/candidates')
@login_required
@admin_required
def admin_candidates():
    candidates = Candidate.query.all()
    return render_template('admin/candidates.html', title='Manage Candidates', candidates=candidates)

@app.route('/admin/candidates/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_candidate():
    form = CandidateForm()
    if form.validate_on_submit():
        candidate = Candidate(
            name=form.name.data,
            party=form.party.data,
            email=form.email.data,
            description=form.description.data,
            photo_url=form.photo_url.data
        )
        db.session.add(candidate)
        db.session.commit()
        
        # Send notification email to the candidate
        if candidate.email and EMAIL_ENABLED:
            try:
                send_candidate_notification(candidate.name, candidate.email, candidate.party)
                logger.info(f"Candidate notification email sent to {candidate.email}")
                flash(f'Candidate added successfully! Notification email sent to {candidate.email}', 'success')
            except Exception as e:
                logger.error(f"Failed to send candidate notification email: {str(e)}")
                flash('Candidate added successfully!', 'success')
        else:
            if candidate.email and not EMAIL_ENABLED:
                logger.info(f"Email notifications disabled. Skipping notification to {candidate.email}")
            flash('Candidate added successfully!', 'success')
        return redirect(url_for('admin_candidates'))
    
    return render_template('admin/add_candidate.html', title='Add Candidate', form=form)

@app.route('/admin/candidates/edit/<int:candidate_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    form = CandidateForm(obj=candidate)
    
    if form.validate_on_submit():
        # Check if email was changed to send notification
        email_changed = candidate.email != form.email.data and form.email.data
        
        candidate.name = form.name.data
        candidate.party = form.party.data
        candidate.email = form.email.data
        candidate.description = form.description.data
        candidate.photo_url = form.photo_url.data
        db.session.commit()
        
        # Send notification if email was updated
        if email_changed and EMAIL_ENABLED:
            try:
                send_candidate_notification(candidate.name, candidate.email, candidate.party)
                logger.info(f"Candidate update notification email sent to {candidate.email}")
                flash(f'Candidate updated successfully! Notification email sent to {candidate.email}', 'success')
            except Exception as e:
                logger.error(f"Failed to send candidate update notification email: {str(e)}")
                flash('Candidate updated successfully!', 'success')
        else:
            if email_changed and not EMAIL_ENABLED:
                logger.info(f"Email notifications disabled. Skipping update notification to {candidate.email}")
            flash('Candidate updated successfully!', 'success')
        return redirect(url_for('admin_candidates'))
    
    return render_template('admin/edit_candidate.html', title='Edit Candidate', form=form, candidate=candidate)

@app.route('/admin/candidates/delete/<int:candidate_id>', methods=['POST'])
@login_required
@admin_required
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Check if candidate has votes
    if Vote.query.filter_by(candidate_id=candidate_id).count() > 0:
        flash('Cannot delete candidate with existing votes!', 'danger')
        return redirect(url_for('admin_candidates'))
    
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('admin_candidates'))

# Voter routes
@app.route('/voter/dashboard')
@login_required
def voter_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    candidates = Candidate.query.all()
    vote_form = VoteForm()
    
    return render_template('voter/dashboard.html', title='Vote', candidates=candidates, vote_form=vote_form)

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    if current_user.role == 'admin':
        abort(403)
    
    if current_user.voted:
        flash('You have already cast your vote!', 'warning')
        return redirect(url_for('results'))
    
    form = VoteForm()
    if form.validate_on_submit():
        candidate_id = form.candidate_id.data
        candidate = Candidate.query.get(candidate_id)
        
        if not candidate:
            flash('Invalid candidate selection!', 'danger')
            return redirect(url_for('voter_dashboard'))
        
        vote = Vote(voter_id=current_user.id, candidate_id=candidate_id)
        current_user.voted = True
        
        db.session.add(vote)
        db.session.commit()
        
        flash('Your vote has been recorded successfully!', 'success')
        return redirect(url_for('results'))
    
    flash('Invalid form submission!', 'danger')
    return redirect(url_for('voter_dashboard'))

@app.route('/results')
def results():
    candidates = Candidate.query.all()
    total_votes = Vote.query.count()
    
    candidate_data = []
    for candidate in candidates:
        vote_count = candidate.vote_count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        candidate_data.append({
            'id': candidate.id,
            'name': candidate.name,
            'party': candidate.party,
            'votes': vote_count,
            'percentage': round(percentage, 2)
        })
    
    # Sort by vote count (descending)
    candidate_data.sort(key=lambda x: x['votes'], reverse=True)
    
    return render_template('results.html', title='Results', candidates=candidate_data, total_votes=total_votes)

@app.route('/api/results')
def api_results():
    candidates = Candidate.query.all()
    total_votes = Vote.query.count()
    
    data = {
        'labels': [candidate.name for candidate in candidates],
        'datasets': [{
            'data': [candidate.vote_count() for candidate in candidates],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)',
                'rgba(199, 199, 199, 0.7)',
                'rgba(83, 102, 255, 0.7)',
                'rgba(40, 159, 64, 0.7)',
                'rgba(210, 199, 199, 0.7)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(199, 199, 199, 1)',
                'rgba(83, 102, 255, 1)',
                'rgba(40, 159, 64, 1)',
                'rgba(210, 199, 199, 1)'
            ],
            'borderWidth': 1
        }]
    }
    
    return jsonify(data)

# Create an admin user if none exists
@app.route('/setup-admin', methods=['GET', 'POST'])
def setup_admin():
    # Check if admin already exists
    admin_exists = User.query.filter_by(role='admin').first() is not None
    
    if admin_exists:
        flash('Admin account already exists!', 'info')
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        admin = User(
            username=form.username.data,
            email=form.email.data,
            role='admin'
        )
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Admin account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Create Admin', form=form)
