from app import create_app

app = create_app()

if __name__ == "__main__": # Inicialização da aplicação na porta 8530
    app.run(host='0.0.0.0', debug=True, port=8530)
