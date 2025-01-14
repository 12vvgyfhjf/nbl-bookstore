from flask import Flask, render_template, request, abort
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="nbl_db"
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Home route to display the list of books by category
@app.route("/")
def index():
    category = request.args.get("category", "All")  # Default category is "All"
    search_query = request.args.get("search", "").strip()  # Get search query if present
    
    conn = get_db_connection()
    if not conn:
        return "Database connection failed. Please check the configuration!", 500
    cursor = conn.cursor(dictionary=True)

    if search_query:  # If there's a search query, filter by title or author
        cursor.execute(
            "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s", 
            ('%' + search_query + '%', '%' + search_query + '%')
        )
    elif category == "All":
        cursor.execute("SELECT * FROM books")
    else:
        cursor.execute("SELECT * FROM books WHERE category = %s", (category,))
    
    books = cursor.fetchall()
    conn.close()

    # Get new books added in the current month
    current_month = datetime.now().month
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE MONTH(date_added) = %s", (current_month,))
    new_books = cursor.fetchall()
    conn.close()

    return render_template("index.html", books=books, new_books=new_books, category=category, search_query=search_query)

# Book details route
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    conn = get_db_connection()
    if not conn:
        return "Database connection failed. Please check the configuration!", 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    conn.close()

    if not book:
        abort(404, description="Book not found!")

    return render_template("book_detail.html", book=book)

if __name__ == "__main__":
    app.run(debug=True)
