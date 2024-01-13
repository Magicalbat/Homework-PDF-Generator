from flask import Flask, stream_with_context, Response, request, render_template

from pagegenerator import PageGenerator

app = Flask(__name__)#, static_folder="/static")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/guide")
def guide():
    return render_template("guide.html")

@app.route("/generator")
def generate_pdf():
    @stream_with_context
    def generate():
        # ?problems=Section: 4-6, Pages: 287-293, Problems: 8, 9, 10, 11-16, 20-26 even, 31-37 odd, 10-25 every 5&box_num=3,3&bg_color=249,255,247
        box_num = (2, 3)
        bg_color = (255, 255, 255)
        if "box_num" in request.args:
            box_num = tuple([int(s) for s in request.args["box_num"].split(',')])
        if "bg_color" in request.args:
            bg_color = tuple([int(s) for s in request.args["bg_color"].split(',')])

        #(249, 255, 247)
        pg = PageGenerator(request.args["problems"], 864, (0.125, 0.25/3), box_num, bg_color)
        yield pg.create_pdf()
    return Response(generate(), mimetype="application/pdf")

def main():
    app.run(host='0.0.0.0', port=81)

if __name__ == "__main__":
    main()
