from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import sqlite3
import csv
from io import StringIO
import io

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = 'Secret!1234'

conn = sqlite3.connect('assets.db')
c = conn.cursor()

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT)''')

# Create assets table
c.execute('''CREATE TABLE IF NOT EXISTS assets
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, 
             unique_id TEXT, po_number TEXT, acquisition_date DATE, maintenance_history TEXT)''')

# Create user_assets table to establish many-to-many relationship
c.execute('''CREATE TABLE IF NOT EXISTS user_assets
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, asset_id INTEGER,
             FOREIGN KEY(user_id) REFERENCES users(id),
             FOREIGN KEY(asset_id) REFERENCES assets(id))''')

conn.commit()
conn.close()

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/import_assets', methods=['POST'])
def import_assets():
    # Get the uploaded file from the request
    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('import_assets'))

    if file:
        # Wrap the file object in TextIOWrapper to ensure it's opened in text mode
        csv_data = csv.reader(io.TextIOWrapper(file, encoding='utf-8'))

        # Skip the header row
        next(csv_data, None)

        # Establish a connection to the database
        conn = sqlite3.connect('assets.db')
        c = conn.cursor()

        try:
            for row in csv_data:
                name = row[1]
                category = row[2]
                unique_id = row[3]
                po_number = row[4]
                acquisition_date = row[5]

                # Insert data into the assets table (excluding id column)
                c.execute('INSERT INTO assets (name, category, unique_id, po_number, acquisition_date) VALUES (?, ?, '
                          '?, ?, ?)',
                          (name, category, unique_id, po_number, acquisition_date))

            conn.commit()
            flash('Data imported successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('view_assets'))

    flash('Invalid file format', 'error')
    return redirect(url_for('import_assets'))


@app.route('/')
def welcome():
    return render_template('welcome.html')


# Route to export assets as CSV
@app.route('/export_assets')
def export_assets():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM assets')
    assets = c.fetchall()
    conn.close()

    # Prepare CSV data
    csv_data = [['ID', 'Name', 'Category', 'Unique ID', 'PO Number', 'Acquisition Date']]
    for asset in assets:
        csv_data.append(asset)

    # Create a CSV response
    output = StringIO()
    csvwriter = csv.writer(output)
    csvwriter.writerows(csv_data)

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=assets.csv'
    response.headers['Content-type'] = 'text/csv'

    return response


@app.route('/remove_asset/<int:user_asset_id>', methods=['POST'])
def remove_asset(user_asset_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    try:
        # Get asset_id associated with the user_asset_id
        c.execute('SELECT asset_id FROM user_assets WHERE id = ?', (user_asset_id,))
        asset_id = c.fetchone()[0]

        # Remove the user-asset association from the user_assets table
        c.execute('DELETE FROM user_assets WHERE id = ?', (user_asset_id,))

        # Check if the asset is associated with any other users
        c.execute('SELECT COUNT(*) FROM user_assets WHERE asset_id = ?', (asset_id,))
        count = c.fetchone()[0]

        # If the asset is not associated with any other users, you can also remove the asset from the assets table
        if count == 0:
            c.execute('DELETE FROM assets WHERE id = ?', (asset_id,))

        conn.commit()
        flash('Asset removed from the user successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('view_user_assets'))


@app.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user(user_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    try:
        # Remove user-asset associations first (if applicable)
        c.execute('DELETE FROM user_assets WHERE user_id = ?', (user_id,))

        # Remove the user from the users table
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))

        conn.commit()
        flash('User removed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('view_user_assets'))


@app.route('/assign_assets', methods=['GET', 'POST'])
def assign_assets():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM assets')
    assets = c.fetchall()

    c.execute('SELECT * FROM users')
    users = c.fetchall()

    if request.method == 'POST':
        asset_id = request.form['asset_id']
        user_id = request.form['user_id']

        # Add logic to assign asset to user in the database
        c.execute('INSERT INTO user_assets (user_id, asset_id) VALUES (?, ?)', (user_id, asset_id))

        conn.commit()
        conn.close()

        flash('Asset assigned successfully!', 'success')
        return redirect(url_for('assign_assets'))

    conn.close()
    return render_template('assign_assets.html', assets=assets, users=users)


@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        category = request.form['category']
        unique_id = request.form['unique_id']
        po_number = request.form['po_number']
        acquisition_date = request.form['acquisition_date']

        # Insert asset into the database
        conn = sqlite3.connect('assets.db')
        c = conn.cursor()
        c.execute(
            'INSERT INTO assets (name, category, unique_id, po_number, acquisition_date, maintenance_history) VALUES (?, ?, ?, ?, ?, ?)',
            (name, category, unique_id, po_number, acquisition_date, ''))
        asset_id = c.lastrowid  # Get the ID of the newly added asset

        # Add logic to assign asset to user in the database
        user_id = request.form['user_id']
        c.execute('INSERT INTO user_assets (user_id, asset_id) VALUES (?, ?)', (user_id, asset_id))

        conn.commit()
        conn.close()

        flash('Asset added successfully and assigned to user!', 'success')
        return redirect(url_for('assign_assets'))


    return render_template('add_asset.html')


@app.route('/view_user_assets', methods=['GET', 'POST'])
def view_user_assets():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()

    user_assets = []
    if request.method == 'POST':
        user_id = request.form['user_id']
        c.execute(
            'SELECT * FROM user_assets JOIN assets ON user_assets.asset_id = assets.id WHERE user_assets.user_id = ?',
            (user_id,))
        user_assets = c.fetchall()

    conn.close()
    return render_template('view_user_assets.html', users=users, user_assets=user_assets)


@app.route('/edit_asset/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()

    # Fetch the asset details from the database
    c.execute('SELECT * FROM assets WHERE id = ?', (asset_id,))
    asset = c.fetchone()

    if asset is None:
        abort(404)  # Asset not found, return a 404 error

    asset_data = {
        'id': asset[0],
        'name': asset[1],
        'category': asset[2],
        'unique_id': asset[3],
        'po_number': asset[4],
        'acquisition_date': asset[5],
        'maintenance_history': asset[6]
    }

    if request.method == 'POST':
        # Update asset details in the database
        name = request.form['name']
        category = request.form['category']
        unique_id = request.form['unique_id']
        po_number = request.form['po_number']

        c.execute('UPDATE assets SET name = ?, category = ?, unique_id = ?, po_number = ? WHERE id = ?',
                  (name, category, unique_id, po_number, asset_id))

        conn.commit()
        conn.close()

        flash('Asset details updated successfully!', 'success')
        return redirect(url_for('view_assets'))

    conn.close()
    return render_template('edit_asset.html', asset=asset_data)


@app.route('/delete_asset/<int:asset_id>', methods=['GET'])
def delete_asset(asset_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    try:
        # Delete the asset from the assets table
        c.execute('DELETE FROM assets WHERE id = ?', (asset_id,))
        conn.commit()
        flash('Asset deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('view_assets'))


@app.route('/add_users', methods=['GET', 'POST'])
def add_users():
    if request.method == 'POST':
        # Handle user bulk import
        if 'user_file' in request.files:
            print("1")
            user_file = request.files['user_file']
            if user_file.filename != '' and allowed_file(user_file.filename):
                csv_data = csv.reader(io.TextIOWrapper(user_file, encoding='utf-8'))
                next(csv_data, None)
                print("2")

                conn = sqlite3.connect('assets.db')
                c = conn.cursor()

                try:
                    for row in csv_data:
                        username = row[1]
                        email = row[2]
                        c.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))

                    conn.commit()
                    flash('Users imported successfully!', 'success')

                except Exception as e:
                    conn.rollback()
                    flash(f'Error: {str(e)}', 'error')

                finally:
                    conn.close()

        # Handle single user addition
        else:
            # Extract user data from the form
            username = request.form['username']
            email = request.form['email']

            # Insert user into the database
            conn = sqlite3.connect('assets.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
                conn.commit()
                flash('User added successfully!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Error: {str(e)}', 'error')
            finally:
                conn.close()

    return render_template('add_users.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    if request.method == 'POST':
        # Get updated user details from the form
        new_username = request.form['username']
        new_email = request.form['email']

        # Update user details in the database
        c.execute('UPDATE users SET username = ?, email = ? WHERE id = ?', (new_username, new_email, user_id))
        conn.commit()
        conn.close()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('view_users'))

    # Fetch current user details for pre-filling the form
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user)


@app.route('/view_users')
def view_users():
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('view_users.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    try:
        # Remove user-asset associations first (if applicable)
        c.execute('DELETE FROM user_assets WHERE user_id = ?', (user_id,))

        # Remove the user from the users table
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))

        conn.commit()
        flash('User removed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('view_users'))


@app.route('/view_assets', methods=['GET', 'POST'])
def view_assets():
    if request.method == 'POST':
        selected_category = request.form.get('category')
        conn = sqlite3.connect('assets.db')
        c = conn.cursor()

        if selected_category:
            c.execute('SELECT * FROM assets WHERE category = ?', (selected_category,))
        else:
            c.execute('SELECT * FROM assets')

        assets = c.fetchall()
        conn.close()

        assets_list = []
        for asset in assets:
            asset_dict = {
                'id': asset[0],
                'name': asset[1],
                'category': asset[2],
                'unique_id': asset[3],
                'po_number': asset[4],
                'acquisition_date': asset[5]
            }
            assets_list.append(asset_dict)

        return render_template('view_assets.html', assets=assets_list)

    conn = sqlite3.connect('assets.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM assets')
    categories = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template('view_assets.html', categories=categories)


@app.route('/import_user_assets', methods=['POST'])
def import_user_assets():
    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('import_user_assets'))

    if file:
        csv_data = csv.reader(io.TextIOWrapper(file, encoding='utf-8'))
        conn = sqlite3.connect('assets.db')
        c = conn.cursor()

        try:
            for row in csv_data:
                _, user_id, asset_id = row
                c.execute('INSERT INTO user_assets (user_id, asset_id) VALUES (?, ?)', (user_id, asset_id))

            conn.commit()
            flash('User assets imported successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            conn.close()

        return redirect(url_for('view_user_assets'))

    flash('Invalid file format', 'error')
    return redirect(url_for('import_user_assets'))


@app.route('/sql_console', methods=['GET', 'POST'])
def sql_console():
    query_result = None

    if request.method == 'POST':
        # Get the SQL query from the form
        sql_query = request.form['sqlQuery']

        # Establish a connection to the database
        conn = sqlite3.connect('assets.db')
        c = conn.cursor()

        try:
            # Execute the SQL query
            c.execute(sql_query)
            # Fetch results if it's a SELECT query
            if sql_query.strip().lower().startswith('select'):
                query_result = c.fetchall()
            else:
                conn.commit()  # Commit changes for non-SELECT queries
            flash('Query executed successfully!', 'success')
        except Exception as e:
            conn.rollback()
            query_result = f'Error: {str(e)}'
            flash(query_result, 'error')
        finally:
            conn.close()

    return render_template('sql_console.html', query_result=query_result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
