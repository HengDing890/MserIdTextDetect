# README #

This repo is the flask template for the demo of answer type classification for QA over structured data.

# Templates #

## Reuse

If you want to use a same head ("<head>...</head>") in different files. You can create a "head.html" file, then "include" it in other files.

### head.html
```
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Intelligence QA Engine| Demo</title>
    <link rel=stylesheet type=text/css href="{{ url_for('static', filename='styles.css') }}">
    <link rel=stylesheet type=text/css href="{{ url_for('static', filename='chart.css') }}">
</head>
```

### index.html
```
<!DOCTYPE html>
<html>
{% include 'head.html' %}
<body>
...
</body>
</html>
```

## Extend
Extend allows you to build a base “skeleton” template that contains all the common elements of your site and defines blocks that child templates can override.

### index.html (base template)
```
<!DOCTYPE html>
<html>
{% include 'head.html' %}
<body>
    <div id="page">
        <h1>Intelligence Question Answer Engine</h1>
        {% include 'search_bar.html' %}
        <div id="resultContainer">
        {% block result_container %}
        {% endblock %}
        </div>
    </div>
    <p class="credit">Authorized by heng.ding@uis.no</p>
</body>

</html>
```

### answertype.html (child template)
```
{% extends "index.html" %}
{% block result_container %}
<div class="webResult">
    <h2><a href="#">Question: {{query}}</a></h2>
</div>
<div id="answerTypeResult">
    <p style="padding-top: 10px; padding-left:5px;"><a href="#" class="btn btn-red">Excepted Answer Type</a></p>
    <div class="charts">
        {% for r in results %}
        <span style="color: black;">{{r[0]}}:{{r[1]}}</span>
        <div class="charts__chart chart--p{{r[2]}} chart--sm chart--green"></div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```



# Files #
## app.py
```
from flask import Flask
from flask import render_template, request
app = Flask(__name__)

# set all route here
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/answer_type', methods=['POST'])
def answer_type():
    # get query text
    query = request.form['query']
    # add your code here

    # replace results with real results from your model
    results = [("ENTITY", 0.37, 37), ("NUMBER", 0.13, 13),
               ("BOOLEAN", 0.25, 25), ("STRING", 0.04, 4), ("DATE", 0.01, 1)]
    return render_template('answertype.html', results=results, query=query)


if __name__ == '__main__':
    app.run(debug=True)
```

There are two routes in app.py:

@app.route('/') links to index.html

@app.route('/answer_type', methods=['POST']) links to answertype.html
