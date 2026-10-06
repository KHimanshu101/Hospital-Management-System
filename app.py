import os
from flask import Flask, render_template, session
from config import Config
from database.connection import check_db_connection
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Jinja Filters
    @app.template_filter('currency')
    def currency_filter(amount):
        try:
            return f"${float(amount):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('status_badge')
    def status_badge_filter(status):
        badges = {
            'Available': 'bg-success',
            'Scheduled': 'bg-primary',
            'Completed': 'bg-info',
            'Active': 'bg-primary',
            'Discharged': 'bg-secondary',
            'Paid': 'bg-success',
            'Pending': 'bg-warning text-dark',
            'Partial': 'bg-info',
            'Occupied': 'bg-danger',
            'Maintenance': 'bg-secondary',
            'Cancelled': 'bg-danger',
            'No-Show': 'bg-dark'
        }
        css_class = badges.get(str(status), 'bg-secondary')
        return f'<span class="badge {css_class} px-2 py-1">{status}</span>'

    # Make session variables easily available to all templates
    @app.context_processor
    def inject_user_session():
        return dict(
            current_username=session.get('username'),
            current_user_fullname=session.get('user_fullname'),
            current_user_role=session.get('user_role')
        )

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.patients import patients_bp
    from routes.doctors import doctors_bp
    from routes.departments import departments_bp
    from routes.appointments import appointments_bp
    from routes.admissions import admissions_bp
    from routes.beds import beds_bp
    from routes.billing import billing_bp
    from routes.pharmacy import pharmacy_bp
    from routes.reports import reports_bp
    from routes.sql_lab import sql_lab_bp
    from routes.er_viva import er_viva_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(admissions_bp)
    app.register_blueprint(beds_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(sql_lab_bp)
    app.register_blueprint(er_viva_bp)

    # Register Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting CarePoint Hospital Management System...")
    db_ok = check_db_connection()
    if not db_ok:
        logger.warning("\n" + "="*70)
        logger.warning("WARNING: Could not connect to MySQL database!")
        logger.warning("Please run 'python setup_db.py' to initialize the database and ensure MySQL Server is active.")
        logger.warning("="*70 + "\n")
    else:
        logger.info("Successfully connected to MySQL database 'carepoint_hms'.")

    app.run(host='127.0.0.1', port=5000, debug=True)
