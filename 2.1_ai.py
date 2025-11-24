"""
Employee Management System
A comprehensive CLI-based system for managing employee data
Meeting all AIML project requirements
"""

import mysql.connector as sql
import datetime as dt
import sys
import getpass 
import hashlib
import logging

# =============================================
# MODULE 1: DATABASE MANAGEMENT
# =============================================

class DatabaseManager:
    """Handles all database operations and connection management"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup system logging for monitoring"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler('system.log')]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_database(self, host='localhost', user='root'):
        """Establish secure database connection"""
        try:
            db_pw = getpass.getpass("Enter your MySQL 'root' password: ")
            self.connection = sql.connect(host=host, user=user, passwd=db_pw)
            self.cursor = self.connection.cursor()
            self.logger.info("Database connection established")
            print("✓ Database connected successfully")
            return True
        except sql.Error as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def initialize_tables(self):
        """Create database schema with proper design"""
        try:
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS employee_management")
            self.cursor.execute("USE employee_management")
            
            # Employees table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id INT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(50),
                    position VARCHAR(50),
                    salary DECIMAL(12, 2),
                    age INT,
                    join_date DATE,
                    email VARCHAR(100)
                )
            """)
            
            # Performance records
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    record_id INT AUTO_INCREMENT PRIMARY KEY,
                    employee_id INT,
                    performance_rating INT,
                    comments TEXT,
                    review_date DATE,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            """)
            
            # User authentication
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(50) PRIMARY KEY,
                    password_hash VARCHAR(64) NOT NULL,
                    role VARCHAR(20) DEFAULT 'employee'
                )
            """)
            
            self.connection.commit()
            self.logger.info("Database tables initialized")
            print("✓ Database tables created successfully")
            return True
            
        except sql.Error as e:
            print(f"✗ Table creation failed: {e}")
            return False

# =============================================
# MODULE 2: AUTHENTICATION MANAGEMENT  
# =============================================

class AuthManager:
    """Handles user registration, login, and security"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password):
        """Secure password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self):
        """User registration with validation"""
        print("\n" + "="*40)
        print("USER REGISTRATION")
        print("="*40)
        
        username = input("Enter username: ").strip()
        if not username:
            print("✗ Username cannot be empty")
            return False
        
        # Check existing user
        self.db.cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if self.db.cursor.fetchone():
            print("✗ Username already exists")
            return False
        
        password = input("Enter password: ").strip()
        if len(password) < 4:
            print("✗ Password must be at least 4 characters")
            return False
        
        hashed_pw = self.hash_password(password)
        
        try:
            self.db.cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            self.db.connection.commit()
            print("✓ User registered successfully!")
            return True
        except sql.Error as e:
            print(f"✗ Registration failed: {e}")
            return False
    
    def login_user(self):
        """User authentication"""
        print("\n" + "="*40)
        print("USER LOGIN")
        print("="*40)
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        hashed_pw = self.hash_password(password)
        
        self.db.cursor.execute(
            "SELECT username FROM users WHERE username = %s AND password_hash = %s",
            (username, hashed_pw)
        )
        
        if self.db.cursor.fetchone():
            print("✓ Login successful!")
            return True
        else:
            print("✗ Invalid credentials")
            return False

# =============================================
# MODULE 3: EMPLOYEE OPERATIONS
# =============================================

class EmployeeOperations:
    """Handles all employee CRUD operations and reporting"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def add_employee(self):
        """Add new employee with validation"""
        print("\n--- ADD NEW EMPLOYEE ---")
        try:
            emp_id = int(input("Employee ID: "))
            name = input("Full Name: ").strip()
            department = input("Department: ").strip()
            position = input("Position: ").strip()
            salary = float(input("Salary: "))
            age = int(input("Age: "))
            email = input("Email: ").strip()
            
            # Validate inputs
            if not name or not department:
                print("✗ Name and department are required")
                return
            
            if age < 18 or age > 65:
                print("✗ Age must be between 18-65")
                return
            
            # Check duplicate ID
            self.db.cursor.execute("SELECT employee_id FROM employees WHERE employee_id = %s", (emp_id,))
            if self.db.cursor.fetchone():
                print("✗ Employee ID already exists")
                return
            
            # Insert employee
            self.db.cursor.execute("""
                INSERT INTO employees (employee_id, name, department, position, salary, age, join_date, email)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), %s)
            """, (emp_id, name, department, position, salary, age, email))
            
            self.db.connection.commit()
            print("✓ Employee added successfully!")
            
        except ValueError:
            print("✗ Invalid input format. Please check your inputs.")
        except sql.Error as e:
            print(f"✗ Database error: {e}")
    
    def view_all_employees(self):
        """Display all employees in formatted table"""
        print("\n--- ALL EMPLOYEES ---")
        self.db.cursor.execute("""
            SELECT employee_id, name, department, position, salary, age, email 
            FROM employees ORDER BY employee_id
        """)
        employees = self.db.cursor.fetchall()
        
        if not employees:
            print("No employees found in database")
            return
        
        # Formatted table header
        print(f"{'ID':<6} {'Name':<20} {'Department':<15} {'Position':<15} {'Salary':<12} {'Age':<4} {'Email':<25}")
        print("-" * 100)
        
        for emp in employees:
            emp_id, name, dept, position, salary, age, email = emp
            print(f"{emp_id:<6} {name:<20} {dept:<15} {position:<15} {salary:<12.2f} {age:<4} {email:<25}")
    
    def update_salary(self):
        """Update employee salary with percentage increase"""
        print("\n--- UPDATE SALARY ---")
        emp_id = input("Enter Employee ID: ").strip()
        
        if not emp_id.isdigit():
            print("✗ Invalid Employee ID")
            return
        
        try:
            # Check if employee exists
            self.db.cursor.execute("SELECT name, salary FROM employees WHERE employee_id = %s", (int(emp_id),))
            employee = self.db.cursor.fetchone()
            
            if not employee:
                print("✗ Employee not found")
                return
            
            name, current_salary = employee
            print(f"Current salary for {name}: ${current_salary:.2f}")
            
            increase_percent = float(input("Enter percentage increase (e.g., 10 for 10%): "))
            new_salary = current_salary * (1 + increase_percent/100)
            
            self.db.cursor.execute(
                "UPDATE employees SET salary = %s WHERE employee_id = %s",
                (new_salary, int(emp_id))
            )
            self.db.connection.commit()
            
            print(f"✓ Salary updated successfully! New salary: ${new_salary:.2f}")
            
        except ValueError:
            print("✗ Invalid input format")
        except sql.Error as e:
            print(f"✗ Database error: {e}")
    
    def view_employee_count(self):
        """Display total employee count"""
        self.db.cursor.execute("SELECT COUNT(*) FROM employees")
        count = self.db.cursor.fetchone()[0]
        print(f"\nTotal employees in system: {count}")
    
    def add_performance_review(self):
        """Add performance review for employee"""
        print("\n--- ADD PERFORMANCE REVIEW ---")
        try:
            emp_id = int(input("Employee ID: "))
            rating = int(input("Performance Rating (1-5): "))
            comments = input("Comments: ").strip()
            
            if rating < 1 or rating > 5:
                print("✗ Rating must be between 1-5")
                return
            
            # Verify employee exists
            self.db.cursor.execute("SELECT name FROM employees WHERE employee_id = %s", (emp_id,))
            if not self.db.cursor.fetchone():
                print("✗ Employee ID not found")
                return
            
            self.db.cursor.execute("""
                INSERT INTO performance (employee_id, performance_rating, comments, review_date)
                VALUES (%s, %s, %s, CURDATE())
            """, (emp_id, rating, comments))
            
            self.db.connection.commit()
            print("✓ Performance review added successfully!")
            
        except ValueError:
            print("✗ Invalid input format")
        except sql.Error as e:
            print(f"✗ Database error: {e}")

# =============================================
# MAIN APPLICATION & MENU SYSTEM
# =============================================

def display_main_menu():
    """Display the main system menu"""
    print("\n" + "="*50)
    print("      EMPLOYEE MANAGEMENT SYSTEM")
    print("="*50)
    print(f"Date: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n1. Add New Employee")
    print("2. View All Employees") 
    print("3. Update Employee Salary")
    print("4. View Employee Count")
    print("5. Add Performance Review")
    print("6. Logout")
    print("="*50)

def main():
    """Main application entry point"""
    # Initialize system components
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    
    print("="*60)
    print("       EMPLOYEE MANAGEMENT SYSTEM - STARTUP")
    print("="*60)
    
    # Database connection
    if not db_manager.connect_database():
        sys.exit(1)
    
    # Initialize tables
    if not db_manager.initialize_tables():
        sys.exit(1)
    
    # Authentication flow
    print("\n1. Register new user")
    print("2. Login")
    
    try:
        choice = int(input("\nEnter choice (1-2): "))
        
        if choice == 1:
            if not auth_manager.register_user():
                sys.exit(1)
            # After registration, proceed to login
            if not auth_manager.login_user():
                sys.exit(1)
        elif choice == 2:
            if not auth_manager.login_user():
                sys.exit(1)
        else:
            print("✗ Invalid choice")
            sys.exit(1)
    except ValueError:
        print("✗ Please enter a valid number")
        sys.exit(1)
    
    # Main system loop (after successful login)
    emp_operations = EmployeeOperations(db_manager)
    
    while True:
        display_main_menu()
        
        try:
            choice = int(input("\nEnter your choice (1-6): "))
            
            if choice == 1:
                emp_operations.add_employee()
            elif choice == 2:
                emp_operations.view_all_employees()
            elif choice == 3:
                emp_operations.update_salary()
            elif choice == 4:
                emp_operations.view_employee_count()
            elif choice == 5:
                emp_operations.add_performance_review()
            elif choice == 6:
                print("\nThank you for using Employee Management System!")
                break
            else:
                print("✗ Please enter a number between 1-6")
                
        except ValueError:
            print("✗ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nSystem interrupted by user. Goodbye!")
            break
    
    # Cleanup
    if db_manager.connection and db_manager.connection.is_connected():
        db_manager.cursor.close()
        db_manager.connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()