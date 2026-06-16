from flask import (Flask, render_template, request, redirect, url_for, session, flash)
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'serverkey2018@gmail.com'
app.config['MAIL_PASSWORD'] = 'mlkdrcrjnoimnclw'

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="Hotel_Booking_Website",
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def index():
    return render_template("index.html")

#-----------------------------------------------ADMIN----------------------------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["hotel"] = True
            flash("Login successful!", "success")
            return redirect(url_for("admin_home"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("admin_login.html")

@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/admin_add_hotel", methods=["GET", "POST"])
def admin_add_hotel():
    if request.method == "POST":
        hotel_name = request.form["hotel_name"]
        location = request.form["location"]
        contact = request.form["contact"]
        email = request.form["email"]
        star = request.form["star"]
        password = request.form["password"]

        image = request.files["image"]
        image_filename = None

        if image and image.filename != "":
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO hotels (hotel_name, location, contact, email, star, password, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (hotel_name, location, contact, email, star, password, image_filename))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Hotel added successfully!", "success")
            return redirect(url_for("admin_view_hotel"))
        except pymysql.MySQLError as err:
            flash(f"Error: {err}", "danger")
            return redirect(url_for("admin_add_hotel"))

    return render_template("admin_add_hotel.html")

@app.route("/admin_view_hotel")
def admin_view_hotel():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM hotels")
        hotels = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("admin_view_hotel.html", hotels=hotels)
    except pymysql.MySQLError as err:
        flash(f"Error fetching hotels: {err}", "danger")
        return redirect(url_for("admin_add_hotel"))

@app.route("/admin_edit_hotel/<int:id>", methods=["GET", "POST"])
def admin_edit_hotel(id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "POST":
        hotel_name = request.form["hotel_name"]
        location = request.form["location"]
        contact = request.form["contact"]
        email = request.form["email"]
        star = request.form["star"]
        password = request.form["password"]

        image = request.files["image"]
        image_filename = None

        if image and image.filename != "":
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
            cursor.execute("""
                UPDATE hotels 
                SET hotel_name=%s, location=%s, contact=%s, email=%s, star=%s, password=%s, image_url=%s 
                WHERE id=%s
            """, (hotel_name, location, contact, email, star, password, image_filename, id))
        else:
            cursor.execute("""
                UPDATE hotels 
                SET hotel_name=%s, location=%s, contact=%s, email=%s, star=%s, password=%s 
                WHERE id=%s
            """, (hotel_name, location, contact, email, star, password, id))

        conn.commit()
        flash("Hotel updated successfully!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("admin_view_hotel"))

    cursor.execute("SELECT * FROM hotels WHERE id = %s", (id,))
    hotel = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("admin_edit_hotel.html", hotel=hotel)

@app.route("/admin_delete_hotel/<int:id>")
def admin_delete_hotel(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotels WHERE id = %s", (id,))
        conn.commit()
        flash("Hotel deleted successfully!", "success")
    except pymysql.MySQLError as err:
        flash(f"Error deleting hotel: {err}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("admin_view_hotel"))

@app.route("/admin_view_user")
def admin_view_user():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    except Exception as e:
        print("Error:", e)
        users = []
    finally:
        conn.close()
    return render_template("admin_view_user.html", users=users)

@app.route("/admin_delete_user/<int:id>")
def admin_delete_user(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        print("Error:", e)
        flash("Error deleting user.", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin_view_user"))

#------------------------------------------------HOTEL---------------------------------------

@app.route("/hotel_login", methods=["GET", "POST"])
def hotel_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT * FROM hotels WHERE email=%s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["password"] == password:
            session["hotel_id"] = user["id"]
            session["hotel_name"] = user["hotel_name"]
            session.pop("table_number", None)
            flash(f"Welcome back, {user['hotel_name']}!", "success")
            return redirect(url_for("hotel_home"))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("hotel_login"))

    return render_template("hotel_login.html")

@app.route("/hotel_home")
def hotel_home():
    return render_template("hotel_home.html")

@app.route("/hotel_add_room", methods=["GET", "POST"])
def hotel_add_room():
    if "hotel_id" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("hotel_login"))

    if request.method == "POST":
        room_type = request.form["room_type"]
        price = request.form["price"]
        capacity = request.form["capacity"]
        description = request.form["description"]
        amenities = request.form.getlist("amenities")
        room_image = request.files["image"]

        room_image_filename = None
        if room_image and room_image.filename != "":
            room_image_filename = secure_filename(room_image.filename)
            os.makedirs("static/uploads/rooms", exist_ok=True)
            room_image.save(os.path.join("static/uploads/rooms", room_image_filename))

        hotel_id = session.get("hotel_id")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO rooms (hotel_id, room_type, price, capacity, description, amenities, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            hotel_id, room_type, price, capacity, description,
            ", ".join(amenities), room_image_filename
        ))
        conn.commit()
        room_id = cur.lastrowid

        def save_meals(meal_type):
            names = request.form.getlist(f"{meal_type}_name[]")
            images = request.files.getlist(f"{meal_type}_image[]")
            os.makedirs(f"static/uploads/foods/{meal_type}", exist_ok=True)

            for name, image in zip(names, images):
                image_filename = None
                if image and image.filename != "":
                    image_filename = secure_filename(image.filename)
                    image.save(os.path.join(f"static/uploads/foods/{meal_type}", image_filename))

                cur.execute("""
                    INSERT INTO room_meals (room_id, meal_type, name, image_url)
                    VALUES (%s, %s, %s, %s)
                """, (room_id, meal_type, name, image_filename))

        save_meals("breakfast")
        save_meals("lunch")
        save_meals("dinner")

        conn.commit()
        cur.close()
        conn.close()

        flash("Room and meals added successfully!", "success")
        return redirect(url_for("hotel_add_room"))

    return render_template("hotel_add_room.html")

@app.route("/hotel_view_booking")
def hotel_view_booking():
    if "hotel_id" not in session:
        flash("Please login as hotel to view bookings.", "warning")
        return redirect(url_for("hotel_login"))

    hotel_id = session["hotel_id"]
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch bookings for this hotel
    cur.execute("""
        SELECT 
            b.id,
            u.name,
            u.email,
            u.contact AS phone,
            b.check_in,
            b.check_out,
            b.adults,
            b.children,
            b.guests,
            b.payment_method,
            b.status,
            r.id AS room_id,
            r.room_type
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN users u ON b.user_id = u.id
        WHERE r.hotel_id = %s
        ORDER BY b.id DESC
    """, (hotel_id,))
    bookings = cur.fetchall()

    # Fetch selected meals for all bookings
    if bookings:
        booking_ids = [b['id'] for b in bookings]
        format_strings = ','.join(['%s'] * len(booking_ids))
        cur.execute(f"""
            SELECT bm.booking_id, rm.meal_type, rm.name, rm.image_url
            FROM booking_meals bm
            JOIN room_meals rm ON bm.room_meal_id = rm.id
            WHERE bm.booking_id IN ({format_strings})
        """, tuple(booking_ids))
        meals = cur.fetchall()

        # Map meals to bookings
        for b in bookings:
            b['selected_meals'] = [m for m in meals if m['booking_id'] == b['id']]

    cur.close()
    conn.close()
    return render_template("hotel_view_booking.html", bookings=bookings)

@app.route("/hotel_booking_action/<int:booking_id>/<string:action>")
def hotel_booking_action(booking_id, action):
    if "hotel_id" not in session:
        flash("Please login as hotel.", "warning")
        return redirect(url_for("hotel_login"))

    if action not in ["Approved", "Rejected"]:
        flash("Invalid action.", "danger")
        return redirect(url_for("hotel_view_booking"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE bookings b
        JOIN rooms r ON b.room_id = r.id
        SET b.status = %s
        WHERE b.id = %s AND r.hotel_id = %s
    """, (action, booking_id, session["hotel_id"]))
    conn.commit()
    cur.close()
    conn.close()
    flash(f"Booking {action} successfully.", "success")
    return redirect(url_for("hotel_view_booking"))

@app.route("/hotel_view_payment")
def hotel_view_payment():
    if "hotel_id" not in session:
        flash("Please login to view payments.", "warning")
        return redirect(url_for("hotel_login"))

    hotel_id = session["hotel_id"]

    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT 
            b.id AS booking_id,
            u.name AS user_name,
            u.email AS user_email,
            r.room_type,
            r.price AS amount,
            b.check_in,
            b.check_out,
            b.payment_method,
            b.status,
            h.hotel_name
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        JOIN users u ON b.user_id = u.id
        WHERE h.id = %s AND b.status = 'Paid'
        ORDER BY b.id DESC
    """, (hotel_id,))

    payments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("hotel_view_payment.html", payments=payments)

#--------------------------------------------------USER--------------------------------------
@app.route("/user_register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        contact = request.form["contact"]
        email = request.form["email"]
        dob = request.form["dob"]
        address = request.form["address"]
        gender = request.form["gender"]
        password = request.form["password"]

        photo = request.files["photo"]
        photo_filename = None
        if photo and photo.filename:
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, age, contact, email, dob, address, gender, photo, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, age, contact, email, dob, address, gender, photo_filename, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("user_login"))
        except Exception as e:
            print("Error:", e)
            flash("Error registering user. Please try again.", "danger")
        finally:
            conn.close()
    return render_template("user_register.html")

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            return redirect(url_for("user_home"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("user_login.html")

@app.route("/user_home")
def user_home():
    return render_template("user_home.html")

@app.route("/user_view_hotel")
def user_view_hotel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM hotels")
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("user_view_hotel.html", hotels=hotels)

@app.route("/user_view_rooms/<int:hotel_id>")
def user_view_rooms(hotel_id):
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT rooms.*, hotels.hotel_name, hotels.location, hotels.star
        FROM rooms
        JOIN hotels ON rooms.hotel_id = hotels.id
        WHERE rooms.hotel_id = %s
    """, (hotel_id,))
    rooms = cur.fetchall()

    room_meals_dict = {}
    if rooms:
        room_ids = [room['id'] for room in rooms]
        format_strings = ','.join(['%s'] * len(room_ids))
        cur.execute(f"""
            SELECT * FROM room_meals
            WHERE room_id IN ({format_strings})
        """, tuple(room_ids))
        meals = cur.fetchall()
        for meal in meals:
            room_meals_dict.setdefault(meal['room_id'], {}).setdefault(meal['meal_type'], []).append(meal)

    cur.close()
    conn.close()
    return render_template("user_view_rooms.html", rooms=rooms, room_meals_dict=room_meals_dict)

@app.route("/book_room/<int:room_id>")
def book_room(room_id):
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT rooms.*, hotels.hotel_name, hotels.location 
        FROM rooms
        JOIN hotels ON rooms.hotel_id = hotels.id
        WHERE rooms.id = %s
    """, (room_id,))
    room = cur.fetchone()

    cur.execute("""
        SELECT * FROM room_meals WHERE room_id = %s
    """, (room_id,))
    meals_raw = cur.fetchall()

    room_meals = {}
    for meal in meals_raw:
        room_meals.setdefault(meal['room_id'], {}).setdefault(meal['meal_type'], []).append(meal)

    cur.close()
    conn.close()
    return render_template("user_booking.html", room=room, room_id=room_id, room_meals=room_meals)

@app.route("/confirm_booking/<int:room_id>", methods=["POST"])
def confirm_booking(room_id):
    if "user_id" not in session:
        flash("Please login to book a room.", "warning")
        return redirect(url_for("user_login"))

    check_in = request.form.get("check_in")
    check_out = request.form.get("check_out")
    adults = int(request.form.get("adults", 1))
    children = int(request.form.get("children", 0))
    payment_method = request.form.get("payment_method")
    message = request.form.get("message", "")
    guests = adults + children

    card_number = request.form.get("card_number")
    card_expiry = request.form.get("card_expiry")
    card_cvv = request.form.get("card_cvv")
    card_name = request.form.get("card_name")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT hotel_id FROM rooms WHERE id = %s", (room_id,))
        room = cur.fetchone()
        if not room:
            flash("Selected room does not exist.", "danger")
            return redirect(url_for("user_view_hotel"))

        hotel_id = room["hotel_id"]

        cur.execute("""
            INSERT INTO bookings
            (user_id, room_id, check_in, check_out, adults, children, guests, payment_method, card_number, card_expiry, card_cvv, card_name, message, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"], room_id, check_in, check_out, adults, children, guests,
            payment_method, card_number, card_expiry, card_cvv, card_name, message, "Pending"
        ))

        conn.commit()
        flash("Booking successfully submitted! Await confirmation from the hotel.", "success")
    except Exception as e:
        print("Booking Error:", e)
        flash("Error submitting booking. Please try again.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("user_view_status"))

@app.route("/user_view_payment")
def user_view_payment():
    if "user_id" not in session:
        return redirect(url_for("user_login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT 
            b.id,
            h.hotel_name AS hotel_name,
            r.room_type,
            r.price AS amount,
            b.check_in,
            b.check_out,
            b.status,
            b.payment_method
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        WHERE b.user_id = %s
        ORDER BY b.id DESC
    """, (user_id,))

    payments = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("user_payment.html", payments=payments)

@app.route("/user_view_status")
def user_view_status():
    if "user_id" not in session:
        flash("Please login to view your bookings.", "warning")
        return redirect(url_for("user_login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, r.room_type, h.hotel_name 
        FROM bookings b 
        JOIN rooms r ON b.room_id = r.id 
        JOIN hotels h ON r.hotel_id = h.id 
        WHERE b.user_id = %s
    """, (session["user_id"],))

    bookings = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("user_view_status.html", bookings=bookings)

@app.route("/user_payment_page/<int:booking_id>")
def user_payment_page(booking_id):
    conn = get_db_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute("""
        SELECT b.id, b.check_in, b.check_out, b.payment_method, b.status,
               b.adults, b.children, b.guests,
               h.hotel_name, r.room_type, r.price AS amount
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        WHERE b.id = %s
    """, (booking_id,))

    booking = cur.fetchone()
    cur.close()
    conn.close()

    if not booking:
        flash("Booking not found!", "danger")
        return redirect(url_for("user_view_payment"))

    return render_template("user_payment_page.html", booking=booking)

@app.route("/user_make_payment/<int:booking_id>", methods=["POST"])
def user_make_payment(booking_id):
    card_number = request.form["card_number"]
    card_expiry = request.form["card_expiry"]
    card_cvv = request.form["card_cvv"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE bookings
        SET status='Paid', card_number=%s, card_expiry=%s, card_cvv=%s
        WHERE id=%s
    """, (card_number, card_expiry, card_cvv, booking_id))

    conn.commit()
    cur.close()
    conn.close()

    flash("Payment successful!", "success")
    return redirect(url_for("user_view_payment"))

@app.route("/confirm_payment/<int:booking_id>", methods=["POST"])
def confirm_payment(booking_id):
    if "user_id" not in session:
        flash("Please login to confirm payment.", "warning")
        return redirect(url_for("user_login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status = %s WHERE id = %s", ("Paid", booking_id))
    conn.commit()
    cur.close()
    conn.close()

    flash("Payment successful!", "success")
    return redirect(url_for("user_view_status"))

if __name__ == "__main__":
    app.run(debug=True)