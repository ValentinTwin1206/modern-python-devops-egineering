from bottle import Bottle, response, run

app = Bottle()


@app.route("/")
def index():
    response.content_type = "application/json"
    return {"message": "Hello from tiny webserver"}


def main():
    run(app=app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()