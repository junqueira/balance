import os
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

def index(request):
    r = requests.get('http://httpbin.org/status/418')
    times = int(os.environ.get('TIMES',3))
    print r.text
    return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):
    greeting = Greeting()
    greeting.save()
    greetings = Greeting.objects.all()
    return render(request, 'db.html', {'greetings': greetings})