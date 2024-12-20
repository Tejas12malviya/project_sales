import sqlite3
from fastapi import FastAPI

def create_and_run_sql_file(db_name, sql_file):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        print("Connection established to SQLite database")

        with open(sql_file, 'r') as file:
            sql_script = file.read()

        cursor.executescript(sql_script)
        conn.commit()
        print("SQL script executed successfully")
    except sqlite3.Error as e:
        print(f"Error executing SQL script: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Create an SQL file named 'sales.sql'
    sql_file_path = 'sales.sql'
    # Write or update SQL query in the file which get updated in database. 
    with open(sql_file_path, 'w') as file:
        file.write("""
             ALTER TABLE sales
                   ADD COLUMN total_sales Decimal(10,2);
                   Update sales set total_sales= quantity * price;
    """)

    # Run the SQL file
    create_and_run_sql_file('sales.db', sql_file_path)


# connection of database with FastAPI 
app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('sales.db')
    conn.row_factory = sqlite3.Row
    return conn

# Shows all the sales data
@app.get("/sales")
def read_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    sales = cursor.fetchall()
    conn.close()
    return {"sales": [dict(row) for row in sales]}

# Update the sales data
@app.post("/sales")
def create_sale(product_name:str,category:str|None,quantity: int, price: float, sale_date: str|None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sales (product_name,category,quantity, price,sale_date,total_sales) VALUES (?,?,?,?, ?,?)", (product_name,category,quantity, price,sale_date,quantity*price))
    conn.commit()
    conn.close()
    return {"message": "Sale created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
