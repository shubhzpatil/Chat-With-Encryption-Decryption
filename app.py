from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import os

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

key = 'abcdefghijklmnopqrstuvwxyz'

socketio = SocketIO(app, manage_session=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if (request.method == 'POST'):
        username = request.form['username']
        room = request.form['room']
        # Store the data in session
        session['username'] = username
        session['room'] = room

        return render_template('chat.html', session=session)
    else:
        if (session.get('username') is not None):
            return render_template('chat.html', session=session)
        else:
            return redirect(url_for('index'))


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room')
    join_room(room)
    emit('status', {'msg'}, room=room)


def cipher_encrypt(plain_text, key):
    """Encrypt text."""
    encrypted = ""
    for char in plain_text:
        if char.isupper():  # check if it's an uppercase character.
            index = ord(char) - ord('A')
            # shift the current character by key positions.
            # shifted = (index + key) % 26 + ord('A')
            new = chr(shifted)
            encrypted += new

        elif char.islower():  # check if its a lowecase character.
            # subtract the unicode of 'a' to get index in [0-25) range.
            index = ord(char) - ord('a')
            shifted = (index + key) % 26 + ord('a')
            new = chr(shifted)
            encrypted += new

        elif char.isdigit():
            # if it's a number,shift its actual value
            new = (int(char) + key) % 10
            encrypted += str(new)

        else:
            # if its neither an alphabet nor a number,
            # don't make any change.
            encrypted += char

    return encrypted


def cipher_decrypt(ciphertext, key):
    """Decrypt text."""
    decrypted = ""
    for char in ciphertext:

        if char.isupper():
            c_index = ord(char) - ord('A')
            # shift the current character to left by key positions
            # to get its original position
            c_og_pos = (c_index - key) % 26 + ord('A')

            c_og = chr(c_og_pos)

            decrypted += c_og

        elif char.islower():
            c_index = ord(char) - ord('a')
            c_og_pos = (c_index - key) % 26 + ord('a')
            c_og = chr(c_og_pos)
            decrypted += c_og

        elif char.isdigit():
            # if it's a number,shift its actual value
            c_og = (int(char) - key) % 10
            decrypted += str(c_og)

        else:
            # if its neither an alphabet nor a number,
            # don't make any change.
            decrypted += char

    return decrypted


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room')
    if (message['msg'][0:4] == 'data'):
        emit('message', {'msg': message['msg']}, room=room)
    else:
        mes = cipher_encrypt(message['msg'], 10)
        emit('message', {'msg': "Encrypted Msg" + ' : ' + mes}, room=room)


@socketio.on('text1', namespace='/chat')
def text1(message):
    room = session.get('room')
    mes = cipher_decrypt(message['msg'], 10)
    emit('message', {'msg': "Decrypted Msg" + ' : ' + mes}, room=room)


@app.route('/success', methods=['POST'])
def files():
    if request.method == 'POST':
        if request.form.get('Encrypt'):
            f = request.files['file']
            f.save(f.filename)

            file = open(f.filename, 'rb')
            image = file.read()
            file.close()

            image = bytearray(image)

            key = int(request.form['key'])

            for i, j in enumerate(image):
                image[i] = j ^ key

            file = open('F:/Final/flaskProject/Files/Encrypted_files/' + f.filename, 'wb')
            file.write(image)
            file.close()
            return render_template("Success.html")
        if request.form.get("Decrypt"):
            f = request.files['file']
            f.save(f.filename)
            file = open(f.filename, 'rb')
            image = file.read()
            file.close()

            image = bytearray(image)

            key = int(request.form['key'])

            for i, j in enumerate(image):
                image[i] = j ^ key

            file = open('F:/Final/flaskProject/Files/Decrypted_files/' + f.filename, 'wb')
            file.write(image)
            file.close()
            return render_template("Success1.html")


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    session.clear()


if __name__ == '__main__':
    socketio.run(app)
