from flask import Blueprint, request, jsonify
from database.safoai.database import db_connection
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

bp = Blueprint('waitlist', __name__)

# Email validation
def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Email sending function
def send_email(recipient_email, subject, message_html):
    """Send email to user"""
    try:
        # Configure your email credentials here
        sender_email = Config.SENDER_EMAIL  # Add to config
        sender_password = Config.SENDER_PASSWORD  # Add to config
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Attach HTML version
        msg.attach(MIMEText(message_html, 'html'))
        
        # Send email via SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Route: Join waitlist
@bp.route('/join', methods=['POST'])
def join_waitlist():
    """Add email to waitlist"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        conn, cursor = db_connection()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM Waitlist WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already on waitlist', 'status': 409}), 409
        
        # Send welcome email
        welcome_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #111;">Welcome to Safo AI — The Future of Building Starts Here 🚀</h2>

                <p>Hi {email or 'there'},</p>

                <p>
                    Thank you for joining the Safo AI waitlist — we’re thrilled to have you onboard!
                </p>

                <p>
                    Safo AI is being built for one mission: to remove the friction, overwhelm, and guesswork 
                    from building a business or project. Whether you're an entrepreneur, a founder, a student, 
                    a freelancer, or a builder chasing a big idea, Safo gives you the tools, clarity, and 
                    execution support you need to make real progress faster.
                </p>

                <h3>Here’s what you’ll unlock when Safo AI launches:</h3>

                <p><strong>🚀 An AI Business Assistant That Actually Builds With You</strong><br>
                    Get strategic guidance, answers, plans, and step-by-step execution — all personalized to your idea and stage. No more scattered information or confusing tutorials.
                </p>

                <p><strong>🛠 Project, Code & Product Builder Tools</strong><br>
                    Turn concepts into finished projects. Generate workflows, documentation, prototypes, and even code. Safo reduces the technical barrier so you can focus on shaping your vision.
                </p>

                <p><strong>💸 Founder–Investor Smart Matching</strong><br>
                    We’re introducing a new way for founders and investors to find each other based on traction, interest, and fit — not just luck. Our AI curates the best matches to accelerate your journey.
                </p>

                <p><strong>📚 A Learning Hub Designed for Builders</strong><br>
                    Unlike traditional courses, Safo teaches you by building with you. Learn only what you need, when you need it, with mini-lessons, challenges, and progress tracking.
                </p>

                <h3>Why all this matters:</h3>

                <p>
                    Most tools today are either too fragmented, too static, or too complex. 
                    Safo combines everything into one end-to-end building environment — guiding you, 
                    organizing you, and empowering you to execute faster than ever.
                </p>

                <p>You’ve joined early, and that gives you:</p>
                <ul>
                    <li>✨ Priority access</li>
                    <li>✨ Early feature rollouts</li>
                    <li>✨ Chance to influence the platform</li>
                    <li>✨ Beta-tester perks and exclusive updates</li>
                </ul>

                <p>
                    We’ll notify you soon with behind-the-scenes updates, launch progress, and your early access link.
                </p>

                <p><strong>Welcome to the future of building —<br>The Safo Team</strong></p>
            </body>
        </html>
        """
        
        email_sent = send_email(email, 'Welcome to Our Waitlist', welcome_html)

        if not email_sent:
            conn.close()
            return jsonify({'error': 'Failed to send welcome email', 'status': 500}), 500
        
        # Insert into waitlist
        cursor.execute(
            "INSERT INTO Waitlist (email, status) VALUES (?, ?)",
            (email, 'joined')
        )
        conn.commit()
        
        email_sent = send_email(email, 'Welcome to Our Waitlist', welcome_html)

        if not email_sent:
            conn.close()
            return jsonify({'error': 'Failed to send welcome email', 'status': 500}), 500
        
        
        conn.close()
        
        return jsonify({
            'message': 'Successfully added to waitlist',
            'email': email,
            'status': 201
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Get all waitlist entries
@bp.route('/all', methods=['GET'])
def get_waitlist():
    """Get all waitlist entries with optional filtering"""
    try:
        status = request.args.get('status')  # Optional filter by status
        
        conn, cursor = db_connection()
        
        if status:
            if status not in ['pending', 'invited', 'joined']:
                conn.close()
                return jsonify({'error': 'Invalid status filter'}), 400
            
            cursor.execute("SELECT * FROM Waitlist WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM Waitlist ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        
        waitlist = []
        for row in rows:
            waitlist.append({
                'id': row['id'],
                'email': row['email'],
                'status': row['status'],
                'created_at': row['created_at'],
                'invited_at': row['invited_at'],
                'joined_at': row['joined_at']
            })
        
        conn.close()
        
        return jsonify({
            'total': len(waitlist),
            'waitlist': waitlist
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Send message/invitation to user
@bp.route('/invite/<int:waitlist_id>', methods=['POST'])
def invite_user(waitlist_id):
    """Send invitation message to user on waitlist"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        conn, cursor = db_connection()
        
        # Get user from waitlist
        cursor.execute("SELECT * FROM Waitlist WHERE id = ?", (waitlist_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found on waitlist'}), 404
        
        # Send custom message/invitation
        invitation_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Special Invitation!</h2>
                <p>Hi {user['name'] or 'there'},</p>
                <p>{data['message']}</p>
                <br>
                <p>Best regards,<br>The Team</p>
            </body>
        </html>
        """
        
        email_sent = send_email(user['email'], 'You\'re Invited!', invitation_html)
        
        if email_sent:
            # Update status to invited
            cursor.execute(
                "UPDATE Waitlist SET status = ?, invited_at = ? WHERE id = ?",
                ('invited', datetime.now().isoformat(), waitlist_id)
            )
            conn.commit()
        
        conn.close()
        
        if email_sent:
            return jsonify({
                'message': 'Invitation sent successfully',
                'user_email': user['email'],
                'status': 'invited'
            }), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Mark user as joined
@bp.route('/mark-joined/<int:waitlist_id>', methods=['PUT'])
def mark_joined(waitlist_id):
    """Mark a waitlist user as joined"""
    try:
        conn, cursor = db_connection()
        
        cursor.execute("SELECT * FROM Waitlist WHERE id = ?", (waitlist_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found on waitlist'}), 404
        
        # Update status to joined
        cursor.execute(
            "UPDATE Waitlist SET status = ?, joined_at = ? WHERE id = ?",
            ('joined', datetime.now().isoformat(), waitlist_id)
        )
        conn.commit()
        
        # Send confirmation email
        confirmation_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Welcome Aboard!</h2>
                <p>Hi {user['name'] or 'there'},</p>
                <p>Your account has been activated! You can now access our platform.</p>
                <br>
                <p>Best regards,<br>The Team</p>
            </body>
        </html>
        """
        
        send_email(user['email'], 'Welcome Aboard!', confirmation_html)
        
        conn.close()
        
        return jsonify({
            'message': 'User marked as joined',
            'user_email': user['email'],
            'status': 'joined'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Remove from waitlist
@bp.route('/remove/<int:waitlist_id>', methods=['DELETE'])
def remove_from_waitlist(waitlist_id):
    """Remove user from waitlist"""
    try:
        conn, cursor = db_connection()
        
        cursor.execute("SELECT email FROM Waitlist WHERE id = ?", (waitlist_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found on waitlist'}), 404
        
        cursor.execute("DELETE FROM Waitlist WHERE id = ?", (waitlist_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'User removed from waitlist',
            'user_email': user['email']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Get waitlist statistics
@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get waitlist statistics"""
    try:
        conn, cursor = db_connection()
        
        cursor.execute("SELECT COUNT(*) as total FROM Waitlist")
        total = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as count FROM Waitlist WHERE status = ?", ('pending',))
        pending = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Waitlist WHERE status = ?", ('invited',))
        invited = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Waitlist WHERE status = ?", ('joined',))
        joined = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'total': total,
            'pending': pending,
            'invited': invited,
            'joined': joined
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500