import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def main():
    if len(sys.argv) < 4:
        print("Usage: python create_hod.py <username> <email> <password>")
        sys.exit(1)
        
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    with app.app_context():
        # Check if already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            print("Error: User or email already exists.")
            sys.exit(1)

        user = User(username=username, email=email, password=generate_password_hash(password), role='HOD', department=None)
        db.session.add(user)
        try:
            db.session.commit()
            print(f"HOD User '{username}' created successfully.")
        except Exception as e:
            print(f"Error creating HOD: {e}")

if __name__ == '__main__':
    main()
