from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Start the local development server in debug mode
    app.run(host='127.0.0.1', port=5000, debug=True)
