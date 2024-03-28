from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configure MySQL database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="zubair084",
    database="database"
)

# Function to create database tables
def create_tables():
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        cname VARCHAR(255) PRIMARY KEY,
        no_of_states INT,
        continent VARCHAR(255)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS population_per_year (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cname VARCHAR(255),
        population INT,
        year INT,
        FOREIGN KEY (cname) REFERENCES countries(cname)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS state_p (
        sname VARCHAR(255) PRIMARY KEY,
        cname VARCHAR(255),
        year INT,
        spopulation INT,
        FOREIGN KEY (cname) REFERENCES countries(cname),
        FOREIGN KEY (year) REFERENCES population_per_year(year)
    )
    """)
    db.commit()


# Create database tables
create_tables()

# Serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')

# Serve the population.html file
@app.route('/population.html')
def population():
    return render_template('population.html')

# Serve the manager login page
@app.route('/manager.html')
def manager_login():
    return render_template('manager.html')

# Serve the user login page
@app.route('/user.html')
def user_login():
    return render_template('user.html')

# Serve the country_data.html file
@app.route('/country_data.html')
def country_data():
    return render_template('country_data.html')

# Serve the population_year.html file
@app.route('/population_year.html')
def population_year():
    return render_template('population_year.html')

# Serve the state_data.html file
@app.route('/state_data.html')
def state_data():
    return render_template('state_data.html')

# Handle manager login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'manager' and password == 'manager1209':
        # Successful login, redirect to manager dashboard
        return redirect(url_for('manager_dashboard'))
    else:
        # Failed login, redirect back to manager login page with error message
        return render_template('manager.html', error=True)

# Serve the manager dashboard
@app.route('/manager_database.html')
def manager_dashboard():
    return render_template('manager_database.html')

@app.route('/manage_country', methods=['POST'])
def manage_country():
    operation = request.form['operation']
    cname = request.form['cname'].upper()  # Convert to uppercase
    no_of_states = request.form['no_of_states']
    continent = request.form['continent'].upper()  # Convert to uppercase

    cursor = db.cursor()

    message = ""  # Define message variable

    if operation == 'insert':
        try:
            # Check if no_of_states is an integer
            no_of_states = int(no_of_states)
            cursor.execute("INSERT INTO countries (cname, no_of_states, continent) VALUES (%s, %s, %s)", (cname, no_of_states, continent))
            db.commit()
            message = "Country inserted successfully."
        except ValueError:
            message = "Error: Number of states must be an integer."
        except mysql.connector.IntegrityError:
            message = "Error: Country already exists."

    elif operation == 'alter':
        # Check if the country exists
        cursor.execute("SELECT * FROM countries WHERE cname=%s", (cname,))
        existing_country = cursor.fetchone()
        if existing_country:
            try:
                # Check if no_of_states is an integer
                new_no_of_states = int(request.form['no_of_states'])
                cursor.execute("UPDATE countries SET no_of_states=%s, continent=%s WHERE cname=%s", (new_no_of_states, continent, cname))
                db.commit()
                message = "Country altered successfully."
            except ValueError:
                message = "Error: Number of states must be an integer."
            except mysql.connector.Error as e:
                message = f"Error: {e}"
        else:
            message = "Error: Country does not exist."

    elif operation == 'delete':
        try:
            # Check if the country exists
            cursor.execute("SELECT * FROM countries WHERE cname=%s", (cname,))
            existing_country = cursor.fetchone()
            if existing_country:
                cursor.execute("DELETE FROM countries WHERE cname=%s", (cname,))
                db.commit()
                message = "Country deleted successfully."
            else:
                message = "Error: Country does not exist."
        except mysql.connector.Error as e:
            message = f"Error: {e}"
    cursor.close()

    return render_template('country_data.html', message=message)

@app.route('/manage_population_year', methods=['POST'])
def manage_population_year():
    operation = request.form['operation']
    cname = request.form['cname'].upper()  # Convert to uppercase
    population = request.form['population']
    year = request.form['year']

    cursor = db.cursor()

    message = ""  # Define message variable

    if operation == 'insert':
        try:
            # Check if population and year are integers
            population = int(population)
            year = int(year)
            # Check if cname exists in countries table
            cursor.execute("SELECT * FROM countries WHERE cname=%s", (cname,))
            result = cursor.fetchone()
            if result:
                cursor.execute("INSERT INTO population_per_year (cname, population, year) VALUES (%s, %s, %s)", (cname, population, year))
                db.commit()
                message = "Data inserted successfully."
            else:
                message = "Error: Country does not exist."
        except ValueError:
            message = "Error: Population and year must be integers."

    elif operation == 'alter':
        # Retrieve existing data for the specified country and year
        cursor.execute("SELECT * FROM population_per_year WHERE cname=%s AND year=%s", (cname, year))
        existing_data = cursor.fetchone()
        if existing_data:
            # Allow user to modify the fields they want to change
            new_cname = request.form.get('new_cname', cname)
            new_population = request.form.get('new_population', existing_data[2])
            new_year = request.form.get('new_year', existing_data[3])

            # Check if the provided country name is the same
            if new_cname != cname:
                message = "Error: Cannot change country name."
            else:
                try:
                    # Check if new_population and new_year are integers
                    new_population = int(new_population)
                    new_year = int(new_year)
                    cursor.execute("UPDATE population_per_year SET population=%s, year=%s WHERE cname=%s AND year=%s", (new_population, new_year, cname, year))
                    db.commit()
                    message = "Data altered successfully."
                except ValueError:
                    message = "Error: New population and year must be integers."
        else:
            message = "Error: Data does not exist."

    elif operation == 'delete':
        try:
            cursor.execute("DELETE FROM population_per_year WHERE cname=%s AND year=%s", (cname, year))
            db.commit()
            message = "Data deleted successfully."
        except mysql.connector.Error as e:
            message = f"Error: {e}"

    cursor.close()

    return render_template('population_year.html', message=message)

@app.route('/manage_state_population', methods=['POST'])
def manage_state_population():
    operation = request.form['operation']
    sname = request.form['sname'].upper()  # Convert to uppercase
    cname = request.form['cname'].upper()  # Convert to uppercase
    year = request.form['year']
    spopulation = request.form['spopulation']

    cursor = db.cursor()

    message = ""  # Define message variable

    if operation == 'insert':
        # Check if cname exists in countries table
        cursor.execute("SELECT * FROM countries WHERE cname=%s", (cname,))
        result = cursor.fetchone()
        if result:
            try:
                # Check if spopulation and year are integers
                spopulation = int(spopulation)
                year = int(year)
                cursor.execute("INSERT INTO state_p (sname, cname, year, spopulation) VALUES (%s, %s, %s, %s)", (sname, cname, year, spopulation))
                db.commit()
                message = "Data inserted successfully."
            except ValueError:
                message = "Error: State population and year must be integers."
            except mysql.connector.IntegrityError:
                message = "Error: Data already exists."
        else:
            message = "Error: Country does not exist."

    elif operation == 'alter':
        # Check if state exists for given country and year
        cursor.execute("SELECT * FROM state_p WHERE sname=%s AND cname=%s AND year=%s", (sname, cname, year))
        result = cursor.fetchone()
        if result:
            try:
                # Check if spopulation is an integer
                spopulation = int(spopulation)
                cursor.execute("UPDATE state_p SET spopulation=%s WHERE sname=%s AND cname=%s AND year=%s", (spopulation, sname, cname, year))
                db.commit()
                message = "Data updated successfully."
            except ValueError:
                message = "Error: State population must be an integer."
            except mysql.connector.Error as e:
                message = f"Error: {e}"
        else:
            message = "Error: State does not exist for the given country and year."

    elif operation == 'delete':
        try:
            # Check if year is an integer
            year = int(year)
            cursor.execute("DELETE FROM state_p WHERE cname=%s AND sname=%s AND year=%s", (cname, sname, year))
            db.commit()
            message = "Data deleted successfully."
        except ValueError:
            message = "Error: Year must be an integer."
        except mysql.connector.Error as e:
            message = f"Error: {e}"

    cursor.close()

    return render_template('state_data.html', message=message)

# Route to serve the population.html page
@app.route('/population.html')
def population_page():
    try:
        # Connect to MySQL database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="zubair084",
            database="database"
        )
        
        # Create cursor
        cursor = db.cursor()
        
        # Fetch country data
        cursor.execute("SELECT * FROM countries")
        country_data = cursor.fetchall()
        
        # Fetch population data per year
        cursor.execute("SELECT id, cname, population, year FROM population_per_year")
        population_data = cursor.fetchall()
        
        # Fetch state population data
        cursor.execute("SELECT sname, cname, year, spopulation FROM state_p")
        state_data = cursor.fetchall()
        
        # Close cursor and database connection
        cursor.close()
        db.close()
        
        # Render population.html template with fetched data
        return render_template('population.html', country_data=country_data, population_data=population_data, state_data=state_data)
    
    except mysql.connector.Error as e:
        print("Error fetching data:", e)
        return "Error fetching data"

@app.route('/run_query', methods=['POST'])
def run_query():
    query = request.form['query']
    cursor = db.cursor()

    try:
        cursor.execute(query)
        headers = [desc[0] for desc in cursor.description]
        result = cursor.fetchall()
        return render_template('query_result.html', headers=headers, result=result)
    except mysql.connector.Error as e:
        error_message = f"Error executing query: {e}"
        return render_template('error.html', error_message=error_message)
 
if __name__ == '__main__':
    app.run(debug=True)
