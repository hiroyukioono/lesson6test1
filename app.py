import os
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>BMI計算機</title>

    <style>
        body {
            font-family: sans-serif;
            max-width: 500px;
            margin: 40px auto;
            padding: 20px;
        }

        h1 {
            text-align: center;
        }

        label {
            display: block;
            margin-top: 15px;
        }

        input {
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            margin-top: 5px;
            font-size: 16px;
        }

        button {
            padding: 10px 20px;
            margin-top: 20px;
            margin-right: 10px;
            font-size: 16px;
            cursor: pointer;
        }

        .result {
            margin-top: 25px;
            padding: 15px;
            background: #f0f0f0;
        }
    </style>
</head>

<body>
    <h1>BMI計算機</h1>

    <form method="post">

        <label for="height">身長（cm）</label>
        <input
            type="number"
            id="height"
            name="height"
            step="0.1"
            min="1"
            value="__HEIGHT__"
            required
        >

        <label for="weight">体重（kg）</label>
        <input
            type="number"
            id="weight"
            name="weight"
            step="0.1"
            min="1"
            value="__WEIGHT__"
            required
        >

        <button type="submit">計算する</button>
        <button type="button" onclick="clearInputs()">クリア</button>

    </form>

    __RESULT__

    <script>
        function clearInputs() {
            document.getElementById("height").value = "";
            document.getElementById("weight").value = "";
        }
    </script>

</body>
</html>
"""


def calculate_bmi(height, weight):
    try:
        height = float(height)
        weight = float(weight)

        if height <= 0 or weight <= 0:
            return None

        # cmをmに変換
        height_m = height / 100

        # BMI計算
        bmi = weight / (height_m * height_m)

        # BMI判定
        if bmi < 18.5:
            evaluation = "低体重"
        elif bmi < 25:
            evaluation = "標準"
        elif bmi < 30:
            evaluation = "肥満（1度）"
        elif bmi < 35:
            evaluation = "肥満（2度）"
        elif bmi < 40:
            evaluation = "肥満（3度）"
        else:
            evaluation = "肥満（4度）"

        return bmi, evaluation

    except (ValueError, TypeError, ZeroDivisionError):
        return None


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")

    height = ""
    weight = ""
    result = ""

    if method == "POST":
        try:
            content_length = int(
                environ.get("CONTENT_LENGTH", "0") or 0
            )

            body = environ["wsgi.input"].read(content_length)

            data = parse_qs(body.decode("utf-8"))

            height = data.get("height", [""])[0]
            weight = data.get("weight", [""])[0]

            bmi_result = calculate_bmi(height, weight)

            if bmi_result:
                bmi, evaluation = bmi_result

                result = f"""
                <div class="result">
                    <strong>計算結果</strong>
                    <p>BMI：{bmi:.1f}</p>
                    <p>評価：{evaluation}</p>
                </div>
                """
            else:
                result = """
                <div class="result">
                    身長と体重を正しく入力してください。
                </div>
                """

        except Exception:
            result = """
            <div class="result">
                入力値を確認してください。
            </div>
            """

    # HTML内の値を置き換える
    html = HTML.replace("__HEIGHT__", height)
    html = html.replace("__WEIGHT__", weight)
    html = html.replace("__RESULT__", result)

    response_body = html.encode("utf-8")

    start_response(
        "200 OK",
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(response_body)))
        ]
    )

    return [response_body]


if __name__ == "__main__":
    # Renderでは環境変数PORTが設定される
    port = int(os.environ.get("PORT", 8000))

    # Renderからアクセスできるようにする
    host = "0.0.0.0"

    print(f"Server started: http://localhost:{port}")

    with make_server(host, port, application) as server:
        server.serve_forever()