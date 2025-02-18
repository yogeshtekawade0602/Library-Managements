from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

# Custom exception classes
class DatabaseConnectionError(Exception):
    pass

class BookNotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')

# Initialize Supabase client with error handling
try:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise DatabaseConnectionError("Supabase credentials are missing")
    
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Failed to initialize Supabase client: {str(e)}")
    supabase = None

# Middleware to check database connection
@app.before_request
def check_db_connection():
    if not supabase:
        flash("Database connection is not available", "error")
        return render_template('error.html', error="Database connection failed"), 500

def validate_book_data(data):
    errors = []
    if not data.get('title'):
        errors.append("Title is required")
    if not data.get('author'):
        errors.append("Author is required")
    if not data.get('isbn'):
        errors.append("ISBN is required")
    if errors:
        raise ValidationError(", ".join(errors))

@app.route('/')
def index():
    try:
        books = supabase.table('books').select('*').execute()
        return render_template('index.html', books=books.data)
    except Exception as e:
        flash(f"Error fetching books: {str(e)}", "error")
        return render_template('index.html', books=[])

@app.route('/book/new', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        try:
            book_data = {
                'title': request.form.get('title'),
                'author': request.form.get('author'),
                'isbn': request.form.get('isbn'),
                'is_available': True
            }
            
            # Validate input data
            validate_book_data(book_data)
            
            # Check for duplicate ISBN
            existing_book = supabase.table('books').select('*').eq('isbn', book_data['isbn']).execute()
            if existing_book.data:
                raise ValidationError(f"Book with ISBN {book_data['isbn']} already exists")
            
            # Insert book
            result = supabase.table('books').insert(book_data).execute()
            
            if not result.data:
                raise DatabaseConnectionError("Failed to add book to database")
            
            flash(f'Successfully added "{book_data["title"]}" to the library!', 'success')
            return redirect(url_for('index'))
            
        except ValidationError as e:
            flash(str(e), 'error')
            return render_template('create_book.html', book_data=book_data)
        except Exception as e:
            flash(f'Error adding book: {str(e)}', 'error')
            return render_template('create_book.html', book_data=book_data)
    
    return render_template('create_book.html', book_data={})

@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
def update_book(book_id):
    try:
        # First get the existing book
        existing_book = supabase.table('books').select('*').eq('id', book_id).execute()
        
        if not existing_book.data:
            raise BookNotFoundError(f"Book with ID {book_id} not found")
        
        book = existing_book.data[0]
        
        if request.method == 'POST':
            try:
                book_data = {
                    'title': request.form.get('title'),
                    'author': request.form.get('author'),
                    'isbn': request.form.get('isbn'),
                    'is_available': request.form.get('is_available') == 'on'
                }
                
                # Validate input data
                validate_book_data(book_data)
                
                # Check for duplicate ISBN (excluding current book)
                duplicate_check = supabase.table('books').select('*').eq('isbn', book_data['isbn']).neq('id', book_id).execute()
                if duplicate_check.data:
                    raise ValidationError(f"Another book with ISBN {book_data['isbn']} already exists")
                
                # Update book
                result = supabase.table('books').update(book_data).eq('id', book_id).execute()
                
                if not result.data:
                    raise DatabaseConnectionError("Failed to update book in database")
                
                flash(f'Successfully updated "{book_data["title"]}"!', 'success')
                return redirect(url_for('index'))
                
            except ValidationError as e:
                flash(str(e), 'error')
                return render_template('edit_book.html', book=book_data)
            except Exception as e:
                flash(f'Error updating book: {str(e)}', 'error')
                return render_template('edit_book.html', book=book_data)
        
        return render_template('edit_book.html', book=book)
        
    except BookNotFoundError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error accessing book: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    try:
        # First get the book to be deleted
        book = supabase.table('books').select('title').eq('id', book_id).execute()
        
        if not book.data:
            raise BookNotFoundError(f"Book with ID {book_id} not found")
        
        title = book.data[0]['title']
        
        # Delete the book
        result = supabase.table('books').delete().eq('id', book_id).execute()
        
        if not result.data:
            raise DatabaseConnectionError("Failed to delete book from database")
        
        flash(f'Successfully deleted "{title}" from the library.', 'success')
        
    except BookNotFoundError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting book: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    flash("The requested page was not found", "error")
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    flash("An internal server error occurred", "error")
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True) 