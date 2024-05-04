from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yaris@051014'
app.config['MYSQL_DB'] = 'mydatabase'

# Function to establish MySQL connection
def get_mysql_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        try:
            # Establish connection
            connection = get_mysql_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            account = cursor.fetchone()
            cursor.close()
            connection.close()

            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[1]
                msg = 'Logged in successfully !'
                return render_template('Specialsinsert.html', msg=msg)
            else:
                msg = 'Incorrect username / password !'
        except Exception as e:
            msg = 'An error occurred: ' + str(e)
    return render_template('login.html', msg=msg)

# Logout route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

def insert_specials(user_id, product_type, product_subtype, product_subnametype, product_price,product_quantity):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        query = 'INSERT INTO specials (user_id, ProductType, ProductName, ProductNameType, ProductPrice,ProductQuantity) VALUES (%s, %s, %s, %s, %s,%s)'
        cursor.execute(query, (user_id, product_type, product_subtype, product_subnametype, product_price,product_quantity))
        connection.commit()

        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print('An error occurred:', e)
        return False

@app.route('/insert_specials', methods=['GET', 'POST'])
def insert_specials_route():
    if request.method == 'POST':
        try:
            user_id = session['id']  # Assuming user is logged in and session contains user id

            product_type = request.form['product_type']
            product_price = request.form['product_price']
            product_quantity = request.form['product_quantity']

            product_subtype = request.form.get('product_subtype')
            custom_subtype = request.form.get('custom_subtype')
            if product_subtype == '' and custom_subtype:
                product_subtype = custom_subtype

            # Extract product sub-subtype from form data or custom input
            product_subnametype = request.form.get('product_subnametype')
            custom_subnametype = request.form.get('custom_subnametype')
            if product_subnametype == '' and custom_subnametype:
                product_subnametype = custom_subnametype

            if insert_specials(user_id, product_type, product_subtype, product_subnametype, product_price, product_quantity):
                return 'Data Inserted Successfully'  # Or redirect to a confirmation page
            else:
                return 'Error occurred while inserting data into database'
        except Exception as e:
            print('An error occurred:', e)
            return 'Error occurred while processing request'
    return render_template('Specialsinsert.html')

def insert_recipe(user_id, dish_name, dish_type, dish_sort, dish_time,product_other,description,machinery):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        query = 'INSERT INTO Recipe (user_id, DishName, DishType, DishSort, DishTime,ProductOtherProducts,Description,Machinery) VALUES ( %s, %s,%s,%s, %s, %s, %s,%s)'
        cursor.execute(query, (user_id, dish_name, dish_type, dish_sort, dish_time,product_other,description,machinery))
        connection.commit()

        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print('An error occurred:', e)
        return False

@app.route('/insert_recipe', methods=['GET', 'POST'])
def insert_recipe_route():
    if request.method == 'POST':
        try:
            user_id = session['id']  # Assuming user is logged in and session contains user id

            dish_name = request.form['dish_name']
            dish_type = request.form['dish_type']
            dish_sort = request.form['dish_sort']

            dish_time = request.form['dish_time']

            product_other = request.form['product_other']

            description = request.form['description']
            machinery = request.form['machinery']


            if insert_recipe(user_id, dish_name, dish_type, dish_sort, dish_time,product_other,description,machinery):
                return 'Data Inserted Successfully'  # Or redirect to a confirmation page
            else:
                return 'Error occurred while inserting data into database'
        except Exception as e:
            print('An error occurred:', e)
            return 'Error occurred while processing request'
    return render_template('RecipeMake.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    word1 = request.args.get('word1')
    word2 = request.args.get('word2')
    word3 = request.args.get('word3')
    dishtime = request.args.get('dishtime')
    recipe_id = request.args.get('recipe_id')    # Execute SQL query to search for the word in the specified columns
    connection = get_mysql_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT DishName, DishType, DishSort, DishTime, ProductOtherProducts, Description, Machinery FROM Recipe WHERE ProductOtherProducts LIKE %s AND ProductOtherProducts LIKE %s AND ProductOtherProducts LIKE %s AND DishTime LIKE %s",
        (f"%{word1}%", f"%{word2}%", f"%{word3}%", f"%{dishtime}%"))
    if cursor.description:
        results = cursor.fetchall()
        cursor.close()

        # If there are results, return JSON
        if results:
            # Convert results to a list of dictionaries
            recipes = []
            for row in results:
                recipe = {
                    "DishType": row[1],
                    "DishName": row[0],
                    "DishSort": row[2],
                    "DishTime": row[3],
                    "ProductOtherProducts": row[4],
                    "Description": row[5],
                    "Machinery": row[6]
                }
                recipes.append(recipe)

            return jsonify(recipes)
        else:
            return render_template('searchRecipe.html', message="No recipes found.")
    else:
        # If the cursor was not executed successfully, render HTML template with an error message
        return render_template('searchRecipe.html', message="Error executing query.")


@app.route('/search/search_prices', methods=['GET', 'POST'])
def search_prices():
    # Get the recipe ID from the URL parameters
        recipe_id = request.args.get('recipe_id')

    # Execute SQL queries here and fetch the results for the specific recipe
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute("""
        SELECT ProductPrice, GROUP_CONCAT(ProductNameType SEPARATOR ',') AS ProductNameTypes
FROM (
    SELECT DISTINCT
        s.ProductPrice,
        CASE
            WHEN t.ProductOtherProducts LIKE CONCAT('%', s.ProductNameType, '%') THEN s.ProductNameType
            ELSE s.ProductName
        END AS ProductNameType,
        ROW_NUMBER() OVER (PARTITION BY  s.ProductPrice, s.ProductNameType ORDER BY LENGTH(s.ProductNameType) DESC) AS rn
    FROM Recipe t
    CROSS JOIN Specials s
    WHERE (FIND_IN_SET(s.ProductNameType, REPLACE(t.ProductOtherProducts, ' ', ','))  >0
           OR FIND_IN_SET(s.ProductName, REPLACE(t.ProductOtherProducts, ' ', ',')) =1)
          AND s.ProductNameType IS NOT NULL
          AND t.id = %s
) AS rm
WHERE rn = 1
GROUP BY ProductPrice;  -- Filter by the recipe ID
    """, (recipe_id,))


        if cursor.description:
            results = cursor.fetchall()
            cursor.close()


# If there are results, return JSON
            if results:
                return jsonify(results)
            else:
                return render_template('index.html', message="No results found.")
        else:
# If the cursor was not executed successfully, render HTML template with an error message
            return render_template('index.html', message="Error executing query.")





if __name__ == '__main__':
    app.run(debug=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        try:
            # Establish connection
            connection = get_mysql_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
                connection.commit()
                msg = 'You have successfully registered !'
            cursor.close()
            connection.close()
        except Exception as e:
            msg = 'An error occurred: ' + str(e)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)