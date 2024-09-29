import sqlite3
from flask import Flask, session, request, render_template, redirect, url_for, g

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/reset')
def reset():
    # Clear session to reset all progress (manual reset route)
    session.clear()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    
    # Initialize levels
    level_descriptions = {
        '1': 'In this level Use the "HINT" on top to fill username and find password',
        '2': 'Arrange the alphabets in given order, then use the "HINT" to decode the finded alphabets',
        '3': 'Use the directions in mirrored way to draw, then use the draw reference to find hidden image on the page',
        '4': 'Find binary, Decode binary to decimal, Decode alphabet from decimal, Arrange alphabet to a name and enter',
        '5': 'Solve the final task to win the game.'
    }

    completed_levels = session.get('completed_levels', [])
    return render_template('home2.html', completed_levels=completed_levels, level_descriptions=level_descriptions)

@app.route('/complete_level/<level>')
def complete_level(level):
    if 'completed_levels' not in session:
        session['completed_levels'] = []

    if level not in session['completed_levels']:
        session['completed_levels'].append(level)

    session.modified = True  # Mark the session as modified
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    fixed_username = "'OR'1'='"  # SQL injection for testing
    message = None
    message_class = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        result = db.execute(query).fetchall()
        
        if result:
            # Mark Level 1 complete and unlock Level 2
            return redirect(url_for('complete_level', level='1'))
        else:
            message = 'Invalid credentials!'
            message_class = 'error-message'
            
    return render_template('login1.html', fixed_username=fixed_username, message=message, message_class=message_class)


@app.route('/caesar_cipher_task', methods=['GET', 'POST'])
def caesar_cipher_task():
    shift = 3
    plaintext = "ASSEMBLE"
    ciphertext = ''.join(chr(((ord(char) - 65 + shift) % 26) + 65) for char in plaintext)
    message = None

    if request.method == 'POST':
        user_input = request.form['caesar_input'].upper()
        if user_input == plaintext:
            return redirect(url_for('complete_level', level='2'))  # Mark Level 2 complete
        else:
            message = 'Incorrect! Try again.'

    return render_template('caesar_cipher.html', ciphertext=ciphertext, message=message)

@app.route('/image_task', methods=['GET', 'POST'])
def image_task():
    if request.method == 'POST':
        user_input = request.form.get('user_input')  # Get the user input from the form
        if user_input and user_input.lower() == 'rotcaercra':
            return redirect(url_for('complete_level', level='3'))  # Redirect to decode task
        else:
            return render_template('image_task.html', error="Incorrect answer. Try again.")  # Render with an error message
    return render_template('image_task.html')


@app.route('/decode_task', methods=['GET', 'POST'])
def decode_task():
    if request.method == 'POST':
        final_input = request.form.get('finalInput')
        if final_input and final_input.lower() == 'steve':
            return redirect(url_for('complete_level', level='4'))  # Mark Level 3 complete
        else:
            return render_template('decode_task1.html', error="Incorrect final answer. Please try again!")
    return render_template('decode_task1.html')

@app.route('/final_task')
def final_task():
    return render_template('final_task.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
