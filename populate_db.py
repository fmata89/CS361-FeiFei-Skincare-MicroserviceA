# populate_db.py
from website import create_app, db
from website.models import User, SkincareFormEntry
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    # Create a test user
    if not User.query.filter_by(email='test@example.com').first():
        test_user = User(
            email='test@example.com',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            first_name='Test'
        )
        db.session.add(test_user)
        db.session.commit()

    # Populate the skincare form entries
    entries = [
        SkincareFormEntry(cleanser='Cleanser A', toner='Toner C', moisturizer='Moisturizer B', serum='Serum C',
                          sunscreen='Sunscreen B'),
        SkincareFormEntry(cleanser='Cleanser B', toner='Toner A', moisturizer='Moisturizer C', serum='Serum B',
                          sunscreen='Sunscreen A'),
        SkincareFormEntry(cleanser='Cleanser C', toner='Toner B', moisturizer='Moisturizer A', serum='Serum A',
                          sunscreen='Sunscreen C')
    ]

    db.session.bulk_save_objects(entries)
    db.session.commit()

print("Database populated with test data.")
