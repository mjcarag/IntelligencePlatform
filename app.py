# from flask import Flask, render_template, request, jsonify
# import os
# import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
# from generate_vsm_data import generate_vsm_data_from_csv, get_unique_states_and_users

# app = Flask(__name__)

# CSV_PATH = r"D:\Office Works\VSC\Diagram Template\ProcessMining\Abbyy Timeline Jan-Dec 2024 CO MO TX 2.csv"

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/vsm-data")
# def vsm_data():
#     try:
#         state = request.args.get("state")
#         user = request.args.get("user")
#         min_freq = int(request.args.get("minFreq", 0))

#         elements = generate_vsm_data_from_csv(
#             CSV_PATH,
#             state_filter=state,
#             user_filter=user,
#             min_freq=min_freq
#         )
#         return jsonify(elements)

#     except Exception as e:
#         import traceback
#         print("Error in /vsm-data route:", e)
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500

# @app.route("/available-states")
# def available_states():
#     states, _ = get_unique_states_and_users(CSV_PATH)
#     return jsonify(states)

# @app.route("/available-users")
# def available_users():
#     _, users = get_unique_states_and_users(CSV_PATH)
#     return jsonify(users)

# if __name__ == "__main__":
#     app.run(debug=True)

##################RUNNING THE APP##################

# from flask import Flask, render_template, request, jsonify
# import os
# import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
# from Scripts.generate_vsm_data import generate_vsm_data_from_csv, get_unique_states_and_users,generate_bottleneck_table

# app = Flask(__name__, static_folder='static', template_folder='templates')

# # CSV_PATH = r"D:\Office Works\VSC\Diagram Template\ProcessMining\Abbyy Timeline Jan-Dec 2024 CO MO TX 2.csv"
# CSV_PATH = os.path.join(os.path.dirname(__file__), "data.csv")


# @app.route("/")
# def home():
#     return render_template("process_mining.html")

# @app.route("/process-mining")
# def process_mining():
#     return render_template("process_mining.html")

# @app.route("/vsm-data")
# def vsm_data():
#     state = request.args.get("state")
#     user = request.args.get("user")
#     min_freq = int(request.args.get("minFreq", 0))

#     try:
#         elements = generate_vsm_data_from_csv(
#             CSV_PATH,
#             state_filter=state,
#             user_filter=user,
#             min_freq=min_freq
#         )
#         return jsonify(elements)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/available-states")
# def available_states():
#     states, _ = get_unique_states_and_users(CSV_PATH)
#     return jsonify(states)

# @app.route("/available-users")
# def available_users():
#     _, users = get_unique_states_and_users(CSV_PATH)
#     return jsonify(users)

# @app.route("/bottleneck-tracker")
# def bottleneck_tracker():
#     return render_template("bottleneck.html")

# @app.route("/bottleneck-data")
# def bottleneck_data():
#     mode = request.args.get("mode", "time_to_next")
#     try:
#         data = generate_bottleneck_table(mode)
#         return jsonify(data)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     # app.run(debug=True)
#     from waitress import serve
#     serve(app, host="0.0.0.0", port=8080)
from flask import Flask, render_template, request, jsonify
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))
from generate_vsm_data import (
    generate_vsm_data_from_csv,
    get_unique_states_and_users,
    generate_bottleneck_table
)

app = Flask(__name__, static_folder='static', template_folder='templates')

CSV_PATH = os.path.join(os.path.dirname(__file__), "data.csv")

@app.route("/")
def home():
    return render_template("process_mining.html")

@app.route("/process-mining")
def process_mining():
    return render_template("process_mining.html")

@app.route("/vsm-data")
def vsm_data():
    state = request.args.get("state")
    user = request.args.get("user")
    min_freq = int(request.args.get("minFreq", 0))

    try:
        elements = generate_vsm_data_from_csv(
            CSV_PATH,
            state_filter=state,
            user_filter=user,
            min_freq=min_freq
        )
        return jsonify(elements)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/available-states")
def available_states():
    try:
        states, _ = get_unique_states_and_users(CSV_PATH)
        return jsonify(states)
    except Exception as e:
        return jsonify([])

@app.route("/available-users")
def available_users():
    try:
        _, users = get_unique_states_and_users(CSV_PATH)
        return jsonify(users)
    except Exception as e:
        return jsonify([])

@app.route("/bottleneck-tracker")
def bottleneck_tracker():
    return render_template("bottleneck.html")

@app.route("/bottleneck-data")
def bottleneck_data():
    mode = request.args.get("mode", "time_to_next")
    try:
        data = generate_bottleneck_table(mode, CSV_PATH)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
