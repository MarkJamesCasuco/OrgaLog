from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date
DESCRIPTION_PREVIEW_LENGTH = 50

def create_db():
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        date TEXT,
        location TEXT,
        category TEXT,
        description TEXT
                )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        section TEXT,
        facebook TEXT
                )
    """)
    conn.commit()
    conn.close()

create_db()

app = Flask(__name__)

@app.route('/')
def home():
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    search_query = request.args.get('search')
    category_filter = request.args.get('category')
    date_sort = request.args.get('date_sort')
    query = "SELECT id, title, date, location, category, description FROM events"
    params = []
    today = str(date.today())
    
    if search_query and search_query.strip() and category_filter and category_filter.strip():
        # Both search and category filter
        category_filter = category_filter.strip().title()
        query += " WHERE title LIKE ? AND category=?"
        params.append('%' + search_query + '%')
        params.append(category_filter)

    elif category_filter and category_filter.strip():
        # Category filter mode
        category_filter = category_filter.strip().title()
        query += " WHERE category=?"
        params.append(category_filter)
        
    elif search_query and search_query.strip():
        # Search mode
        query += " WHERE title LIKE ?"
        params.append('%' + search_query + '%')

    if date_sort == 'date_newest':
        query += " ORDER BY date DESC"
    elif date_sort == 'date_oldest':
        query += " ORDER BY date ASC"
    else:
        query += " ORDER BY date DESC"
    cursor.execute(query, params)
    events = [
        {'id': row[0], 'title': row[1], 'date': row[2], 'location': row[3], 'category': row[4], 'description': row[5]} 
        for row in cursor.fetchall()
    ]
    cursor.execute("SELECT * FROM members")
    members = [
        {'id': row[0], 'name': row[1], 'section': row[2], 'facebook': row[3]} 
        for row in cursor.fetchall()
    ]
    cursor.execute("SELECT DISTINCT category FROM events")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('Home.html', 
    events=events, 
    categories=categories, 
    selected_category=category_filter, 
    search_query=search_query, 
    date_sort=date_sort, 
    today=today, 
    members=members,
    description_preview_length=DESCRIPTION_PREVIEW_LENGTH
    )

@app.route('/AddEvent')
def add_event():
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM events")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('AddEvent.html', categories=categories)

@app.route('/SaveEvent', methods=['POST'])
def save_events():
    title = request.form['title']
    date = request.form['date']
    category_dropdown = request.form.get('category-dropdown')
    category_text = request.form.get('category')

    # Use dropdown if selected, otherwise use text input
    if category_dropdown and category_dropdown != 'new' and category_dropdown != '':
        category = category_dropdown.strip().title()
    else:
        category = category_text.strip().title()

    location = request.form['location']
    description = request.form['description']
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (title, date, location, category, description) VALUES (?, ?, ?, ?, ?)",(title, date, location, category, description))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/EditEvent/<int:event_id>')
def edit_event(event_id):
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = cursor.fetchone()
    event = {'id': event[0], 'title': event[1], 'date': event[2], 'location': event[3], 'category': event[4], 'description': event[5]}
    cursor.execute("SELECT DISTINCT category FROM events")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('EditEvent.html', event=event, categories=categories)

@app.route('/UpdateEvent', methods=['POST'])
def update_event():
    title = request.form['title']
    date = request.form['date']
    location = request.form['location']
    description = request.form['description']
    category_dropdown = request.form.get('category-dropdown')
    category_text = request.form.get('category')
    if category_dropdown and category_dropdown != 'new' and category_dropdown != '':
        category = category_dropdown.strip().title()
    else:
        category = category_text.strip().title()
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET title=?, date=?, location=?, category=?, description=? WHERE id=?", (title, date, location, category, description, request.form['id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/DeleteEvent/<int:event_id>')
def delete_event(event_id):
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/EventDetail/<int:event_id>')
def event_detail(event_id):
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE id=?", (event_id,))
    event = cursor.fetchone()
    event = {'id': event[0], 'title': event[1], 'date': event[2], 'location': event[3], 'category': event[4], 'description': event[5]}
    conn.close()
    return render_template('EventDetail.html', event=event)

@app.route('/AddMember')
def add_member():
    return render_template('AddMember.html')

@app.route('/SaveMember', methods=['POST'])
def save_member():
    name = request.form['name']
    section = request.form['section']
    facebook = request.form['facebook']
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name, section, facebook) VALUES (?, ?, ?)",(name, section, facebook))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/EditMember/<int:member_id>')
def edit_member(member_id):
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id=?", (member_id,))
    member = cursor.fetchone()
    member = {'id': member[0], 'name': member[1], 'section': member[2], 'facebook': member[3]}
    conn.close()
    return render_template('EditMember.html', member=member)

@app.route('/UpdateMember', methods=['POST'])
def update_member():
    name = request.form['name']
    section = request.form['section']
    facebook = request.form['facebook']
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET name=?, section=?, facebook=? WHERE id=?", (name, section, facebook, request.form['id']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/DeleteMember/<int:member_id>')
def delete_member(member_id):
    conn = sqlite3.connect('orgalog.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)