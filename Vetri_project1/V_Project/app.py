from flask import Flask, render_template, redirect, request, url_for, session,jsonify
from flask_mysqldb import MySQL
import requests
import _mysql_connector

vj = Flask(__name__, static_url_path='/static')

vj.secret_key = "Vijaymaris07"
vj.config["MYSQL_HOST"] = 'localhost'
vj.config["MYSQL_USER"] = 'root'
vj.config["MYSQL_PASSWORD"] = 'Vijay@006'
vj.config["MYSQL_DB"] = 'admin'

UPLOAD_API_URL = 'http://127.0.0.1:5000/retrieve/'

mysql = MySQL(vj)

def is_loggedin():
    return "Name" in session

@vj.route("/login", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        User_Name = request.form.get("username")
        Pass_word = request.form.get("password")
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM details WHERE name=%s AND password=%s", (User_Name, Pass_word))
        data = cur.fetchone()
        cur.close() 

        if data:
            session["Name"] = User_Name 

            if User_Name == "Vijay":
                return redirect(url_for('product',id=1))  
            else:
                return redirect(url_for('product_detail')) 
        else:
            return "Invalid username or password"  
            
    return render_template("login.html")

@vj.route("/stock")
def table():
    if is_loggedin():
        Name = session.get("Name")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stock")
        data = cur.fetchall()
        cur.close()
        
        if Name == "Vijay":
            return render_template('stock.html', data=data, enumerate=enumerate)
        else:
            return render_template('stock2.html', data=data, enumerate=enumerate)
    else:
        return redirect(url_for('home'))

@vj.route("/", methods=["GET", "POST"])
def Signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM details WHERE name=%s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return render_template("home.html", error="Username already taken. Please choose a different one.")

        # Insert new user
        cur.execute("INSERT INTO details (name, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("home"))

    return render_template("home.html")

@vj.route("/add", methods=["GET", "POST"])
def add_stock():
    stock_name = request.args.get('stock', '')

    if request.method == "POST":
        Stock = request.form.get("stock")
        Quantity = request.form.get("quantity")
        Price = request.form.get("price")
        Total_Value = float(Quantity) * float(Price)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO stock (stock, Quantity, Price, total_value) VALUES (%s, %s, %s, %s)", 
                   (Stock, Quantity, Price, Total_Value))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('table'))

    return render_template("add.html", stock_name=stock_name)  

@vj.route("/edit/<string:No>", methods=["GET", "POST"])
def edit(No):
    if request.method == "POST":
        Stock = request.form.get("stock")
        Quantity = request.form.get("quantity")
        Price = request.form.get("price")  
        Total_Value = float(Quantity) * float(Price) 

        cur = mysql.connection.cursor()
        cur.execute("UPDATE stock SET stock=%s, Quantity=%s, Price=%s, total_value=%s WHERE No=%s", 
                   (Stock, Quantity, Price, Total_Value, No))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("table"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stock WHERE No=%s", (No,))
    data = cur.fetchone()
    cur.close()
    return render_template("edit.html", data=data)

@vj.route("/delete/<string:No>", methods=["GET", "POST"])
def delete(No):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM stock WHERE No=%s", (No,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('table'))

# @vj.route("/retrieve/<string:id>", methods=["GET"])
# def product(id):
#     image_url = f'{UPLOAD_API_URL}{id}'
    

#     print(f'Image URL: {image_url}')  


#     response = requests.get(image_url)
#     if response.status_code == 200:
#         return render_template('product.html', image_url=image_url)
#     else:
#         return "Image not found", 404
@vj.route('/retrieve', methods=['GET'])
def product():
    cur = mysql.connection.cursor()

    sql = "SELECT id, img, filename FROM images"
    cur.execute(sql)
    results = cur.fetchall()   
    cur.close()

    if not results:
        return "No images found", 404  # Handle empty results

    return render_template('product.html', images=results)

@vj.route('/add-details/<int:id>', methods=['GET', 'POST'])
def add_details(id):
    # Fetch the image details for the selected image
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, img, filename FROM images WHERE id = %s", (id,))
    image = cursor.fetchone()
    cursor.close()

    if not image:
        return "Image not found", 404

    if request.method == "POST":

        Quantity = request.form.get("quantity")
        Price = request.form.get("price")

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO inventory (image_id, quantity, price) VALUES (%s, %s, %s)", (id, Quantity, Price))
        mysql.connection.commit() 
        cur.close()


        return redirect(url_for('submit_details'))


    return render_template('add_details.html', image=image)

@vj.route('/show-details', methods=['GET'])
def submit_details():
    try:
        # Fetch all inventory details including image, filename, quantity, and price
        cursor = mysql.connection.cursor()
        sql = """
            SELECT images.id, images.img, images.filename, inventory.quantity, inventory.price 
            FROM inventory 
            JOIN images ON inventory.image_id = images.id
        """
        cursor.execute(sql)
        inventory_data = cursor.fetchall()
        cursor.close()

        # If no data is found
        if not inventory_data:
            return render_template('show_details.html', inventory=[])

        # Format the data to be passed to the template
        inventory_list = []
        for row in inventory_data:
            inventory_list.append({
                'image_id': row[0], # Image ID
                'img': row[1],      # Image path
                'filename': row[2], # Image filename
                'quantity': row[3], # Quantity
                'price': row[4],    # Price
            })

        # Render the template with inventory data
        return render_template('show_details.html', inventory=inventory_list)

    except Exception as e:
        return f"An error occurred: {str(e)}"   
    

@vj.route("/edit_details/<int:id>", methods=["GET", "POST"])
def edit_details(id):
    if request.method == "POST":
        # Update the quantity and price in the inventory
        Quantity = request.form.get("quantity")
        Price = request.form.get("price")

        cur = mysql.connection.cursor()
        cur.execute("UPDATE inventory SET quantity=%s, price=%s WHERE image_id=%s", (Quantity, Price, id))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('submit_details'))

    # Fetch the image details and current inventory details for the selected image
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT images.id, images.img, images.filename, inventory.quantity, inventory.price
        FROM images
        JOIN inventory ON images.id = inventory.image_id
        WHERE images.id = %s
    """, (id,))
    data = cursor.fetchone()
    cursor.close()

    if not data:
        return "Image not found", 404

    # Render the edit form with the existing details
    return render_template("edit_details.html", image=data)

@vj.route('/product-details', methods=['GET'])
def product_detail():
    try:
        # Fetch all inventory details including image, filename, quantity, and price
        cursor = mysql.connection.cursor()
        sql = """
            SELECT images.id, images.img, images.filename, inventory.quantity, inventory.price 
            FROM inventory 
            JOIN images ON inventory.image_id = images.id
        """
        cursor.execute(sql)
        inventory_data = cursor.fetchall()
        cursor.close()

        # If no data is found
        if not inventory_data:
            return render_template('show_details.html', inventory=[])

        # Format the data to be passed to the template
        inventory_list = []
        for row in inventory_data:
            inventory_list.append({
                'image_id': row[0], # Image ID
                'img': row[1],      # Image path
                'filename': row[2], # Image filename
                'quantity': row[3], # Quantity
                'price': row[4],    # Price
            })

        # Render the template with inventory data
        return render_template('product_details.html', inventory=inventory_list)

    except Exception as e:
        return f"An error occurred: {str(e)}"   

if __name__ == "__main__":
    vj.run(debug=True, port=2015)
