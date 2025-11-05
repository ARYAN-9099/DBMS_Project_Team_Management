from esports_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=app.config.get('PORT', 5000)
    )
