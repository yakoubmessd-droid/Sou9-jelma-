from flask import Flask, request, redirect, session, render_template_string
import sqlite3
import os
import time
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "sou9-jilma-secret-2026"

DB = "sou9_jilma.db"

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():

    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            image TEXT,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:

        conn.execute(
            "ALTER TABLE users ADD COLUMN email TEXT"
        )

        conn.commit()

    except sqlite3.OperationalError:

        pass


    admin = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        ("so9na.com",)
    ).fetchone()


    if not admin:

        conn.execute(
            """
            INSERT INTO users
            (
                username,
                password,
                phone,
                email,
                is_admin
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "so9na.com",
                generate_password_hash("yakoub50"),
                "",
                "admin@so9na.com",
                1
            )
        )

    else:

        conn.execute(
            """
            UPDATE users
            SET password = ?,
                is_admin = 1
            WHERE username = ?
            """,
            (
                generate_password_hash("yakoub50"),
                "so9na.com"
            )
        )


    conn.commit()

    conn.close()


CATEGORIES = [
    ("📱", "هواتف"),
    ("💻", "إلكترونيات"),
    ("🚗", "سيارات"),
    ("🏠", "عقارات"),
    ("👕", "ملابس"),
    ("🌾", "فلاحة"),
    ("🐄", "حيوانات"),
    ("🔧", "خدمات"),
    ("🛋️", "أثاث"),
    ("📦", "أخرى")
]
STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<style>

* {
    box-sizing: border-box;
}

html,
body {
    width: 100%;
    min-height: 100%;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    background: #f5f3ff;
    color: #222;
    overflow-x: hidden;
}

/* ================= NAVBAR ================= */

nav {
    width: 100%;
    background: linear-gradient(
        135deg,
        #5b21b6,
        #7c3aed
    );
    color: white;
    padding: 12px 10px;
    box-shadow: 0 3px 12px #0002;
}

.nav-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
}

.logo {
    width: 100%;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

.nav-buttons {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 7px;
    flex-wrap: wrap;
}

.nav-buttons a {
    flex: 1;
    min-width: 65px;
    max-width: 130px;
    text-align: center;
    background: #ffffff20;
    color: white;
    padding: 9px 6px;
    border-radius: 10px;
    text-decoration: none;
    font-size: 13px;
    transition: 0.2s;
}

.nav-buttons a:hover {
    background: #ffffff38;
    transform: translateY(-1px);
}

/* ================= MAIN ================= */

.container {
    width: 100%;
    min-height: calc(100vh - 100px);
    padding: 10px;
}

.hero {
    width: 100%;
    background: white;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px #0001;
}

.hero h1 {
    color: #5b21b6;
    margin-top: 0;
}

/* ================= WELCOME ================= */

.welcome {
    width: 100%;
    background: linear-gradient(
        135deg,
        #ede9fe,
        #ddd6fe
    );
    color: #4c1d95;
    padding: 15px;
    border-radius: 13px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px #0001;
}

/* ================= SEARCH ================= */

.search {
    width: 100%;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

input,
textarea,
select {
    width: 100%;
    padding: 14px;
    border: 1px solid #ddd6fe;
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 16px;
    background: white;
    outline: none;
}

input:focus,
textarea:focus,
select:focus {
    border-color: #7c3aed;
    box-shadow: 0 0 0 2px #7c3aed22;
}

/* ================= BUTTONS ================= */

button,
.btn {
    background: linear-gradient(
        135deg,
        #5b21b6,
        #7c3aed
    );
    color: white;
    border: none;
    padding: 13px 18px;
    border-radius: 10px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
}

button {
    width: auto;
}

.btn-danger {
    background: #dc2626;
}

.btn-blue {
    background: #2563eb;
}

/* ================= PRODUCTS ================= */

.grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(
        2,
        minmax(0, 1fr)
    );
    gap: 9px;
}

.card {
    width: 100%;
    background: white;
    border-radius: 13px;
    overflow: hidden;
    box-shadow: 0 2px 8px #0002;
    transition: 0.2s;
}

.card:hover {
    transform: translateY(-2px);
}

.card img {
    width: 100%;
    height: 145px;
    object-fit: cover;
    display: block;
}

.card-body {
    width: 100%;
    padding: 10px;
}

.card-body h3 {
    font-size: 15px;
    margin: 4px 0 8px;
}

.price {
    color: #6d28d9;
    font-size: 17px;
    font-weight: bold;
}

.category {
    color: #777;
    font-size: 13px;
}

/* ================= FORM ================= */

.form-box {
    width: 100%;
    max-width: 600px;
    margin: 10px auto;
    background: white;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0 2px 10px #0001;
}

.alert {
    background: #fee2e2;
    color: #991b1b;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 12px;
}

/* ================= DETAILS ================= */

.detail {
    width: 100%;
    background: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 2px 10px #0001;
}

.detail img {
    width: 100%;
    max-height: 450px;
    object-fit: contain;
    border-radius: 12px;
}

/* ================= ADMIN ================= */

.admin-header {
    width: 100%;
    background: linear-gradient(
        135deg,
        #5b21b6,
        #7c3aed
    );
    color: white;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.admin-stats {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(
        2,
        1fr
    );
    gap: 8px;
}

.stat {
    background: white;
    border-radius: 13px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 8px #0001;
}

.stat-number {
    font-size: 25px;
    font-weight: bold;
    color: #6d28d9;
}

.category-box {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(
        2,
        1fr
    );
    gap: 8px;
}

.category-item {
    background: white;
    border-radius: 13px;
    padding: 14px 8px;
    text-align: center;
}

.admin-card {
    background: white;
    border-radius: 13px;
    padding: 15px;
    margin: 8px 0;
    box-shadow: 0 2px 8px #0001;
}

.admin-actions {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
}

/* ================= FOOTER ================= */

footer {
    width: 100%;
    text-align: center;
    padding: 25px 10px;
    color: #777;
}

/* ================= PHONE ================= */

@media (max-width: 600px) {

    html,
    body {
        width: 100vw;
        min-width: 100vw;
        max-width: 100vw;
    }

    nav {
        padding: 10px 7px;
    }

    .container {
        width: 100vw;
        padding: 8px;
    }

    .logo {
        font-size: 20px;
    }

    .nav-buttons {
        gap: 5px;
    }

    .nav-buttons a {
        min-width: 60px;
        max-width: none;
        padding: 9px 5px;
        font-size: 12px;
    }

    .grid {
        width: 100%;
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }

    .card img {
        height: 135px;
    }

    .card-body {
        padding: 8px;
    }

    .card-body h3 {
        font-size: 14px;
    }

    .price {
        font-size: 16px;
    }

}

/* ================= SMALL PHONES ================= */

@media (max-width: 360px) {

    .nav-buttons a {
        min-width: 55px;
        font-size: 11px;
        padding: 8px 4px;
    }

    .logo {
        font-size: 18px;
    }

}

</style>
"""


@app.route("/")
def home():

    if not session.get("user_id"):

        return redirect("/login")


    search = request.args.get(
        "search",
        ""
    )

    category = request.args.get(
        "category",
        ""
    )


    conn = get_db()


    query = """
        SELECT *
        FROM ads
        WHERE 1=1
    """


    params = []


    if search:

        query += """
            AND (
                title LIKE ?
                OR description LIKE ?
                OR location LIKE ?
            )
        """

        word = "%" + search + "%"

        params.extend([
            word,
            word,
            word
        ])


    if category:

        query += """
            AND category = ?
        """

        params.append(category)


    query += """
        ORDER BY id DESC
    """


    ads = conn.execute(
        query,
        params
    ).fetchall()


    conn.close()


    return render_template_string(

        STYLE + """

        <nav>

    <div class="nav-container">

        <div class="logo">
            🛒 Sou9na 🇹🇳
        </div>

        <div class="nav-buttons">

            <a href="/">
                🏠 الرئيسية
            </a>

            <a href="/profile">
                👤 حسابي
            </a>

            <a href="/add">
                📢 نشر
            </a>

            {% if session.get("is_admin") %}

                <a href="/admin">
                    🛡️ Admin
                </a>

            {% endif %}

            <a href="/logout">
                🚪 خروج
            </a>

        </div>

    </div>

</nav>


        <div class="container">

            <div class="welcome">

                👋 مرحباً

                <b>
                    {{ session.get("username") }}
                </b>

                <br>

                أهلاً بيك في Sou9na 🇹🇳

            </div>


            <div class="hero">

                <h1>
                    سوقنا 🛒
                </h1>

                <p>
                    بيع وشراء بسهولة 🇹🇳
                </p>


                <form
                    class="search"
                    method="GET"
                >

                    <input
                        name="search"
                        placeholder="🔍 شنوة تحب تلقى؟"
                        value="{{ search }}"
                    >


                    <select name="category">

                        <option value="">
                            📂 كل التصنيفات
                        </option>


                        {% for icon, c in categories %}

                            <option
                                value="{{ c }}"
                                {% if category == c %}
                                selected
                                {% endif %}
                            >

                                {{ icon }}
                                {{ c }}

                            </option>

                        {% endfor %}

                    </select>


                    <button type="submit">

                        🔍 بحث

                    </button>

                </form>

            </div>


            <div class="grid">

                {% for ad in ads %}

                    <a
                        href="/ad/{{ ad['id'] }}"
                        style="
                            text-decoration:none;
                            color:inherit;
                        "
                    >

                        <div class="card">

                            {% if ad['image'] %}

                                <img
                                    src="/static/uploads/{{ ad['image'].split('|')[0] }}"
                                >

                            {% else %}

                                <div style="
                                    height:145px;
                                    display:flex;
                                    align-items:center;
                                    justify-content:center;
                                    background:#ddd;
                                    font-size:35px;
                                ">

                                    📷

                                </div>

                            {% endif %}


                            <div class="card-body">

                                <h3>
                                    {{ ad['title'] }}
                                </h3>


                                <div class="price">

                                    💰
                                    {{ ad['price'] }}
                                    د.ت

                                </div>


                                <p class="category">

                                    📂
                                    {{ ad['category'] }}

                                    •

                                    📍
                                    {{ ad['location'] }}

                                </p>


                                <span class="btn">

                                    👁️ التفاصيل

                                </span>

                            </div>

                        </div>

                    </a>

                {% else %}

                    <p>
                        ما فماش إعلانات حالياً.
                    </p>

                {% endfor %}

            </div>

        </div>


        <footer>

            Sou9na © 2026 🇹🇳

        </footer>

        """,

        ads=ads,

        search=search,

        category=category,

        categories=CATEGORIES

    )
@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect("/")

    error = ""

    if request.method == "POST":

        identifier = request.form.get(
            "identifier",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = ?
               OR LOWER(username) = ?
            """,
            (
                identifier,
                identifier
            )
        ).fetchone()

        conn.close()

        valid = False

        if user:

            try:

                valid = check_password_hash(
                    user["password"],
                    password
                )

            except (ValueError, TypeError):

                valid = (
                    user["password"]
                    == password
                )

        if valid:

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            session["is_admin"] = user["is_admin"]

            return redirect("/")

        error = "الإيميل أو اسم المستخدم أو كلمة السر غلط."


    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

                <div style="
                    text-align:center;
                    background:linear-gradient(
                        135deg,
                        #5b21b6,
                        #7c3aed
                    );
                    color:white;
                    padding:18px;
                    border-radius:14px;
                    margin-bottom:18px;
                ">

                    <h1>
                        Sou9na 🇹🇳
                    </h1>

                    <p>
                        مرحبا بيك 👋
                    </p>

                </div>


                <h2>
                    تسجيل الدخول 🔐
                </h2>


                {% if error %}

                    <div class="alert">

                        {{ error }}

                    </div>

                {% endif %}


                <form method="POST">

                    <input
                        type="text"
                        name="identifier"
                        placeholder="📧 الإيميل أو اسم المستخدم"
                        required
                    >


                    <input
                        type="password"
                        name="password"
                        placeholder="🔐 كلمة السر"
                        required
                    >


                    <button
                        type="submit"
                        style="width:100%;"
                    >

                        🚀 دخول

                    </button>

                </form>


                <br>


                <a href="/register">

                    ما عندكش حساب؟
                    إنشاء حساب

                </a>

            </div>

        </div>

        """,

        error=error

    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if session.get("user_id"):
        return redirect("/")

    error = ""

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        if not email or not password:

            error = "اكتب الإيميل وكلمة السر."

        elif "@" not in email:

            error = "الإيميل غير صحيح."

        elif len(password) < 6:

            error = "كلمة السر لازم تكون 6 أحرف على الأقل."

        else:

            conn = get_db()

            existing = conn.execute(
                """
                SELECT id
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()


            if existing:

                conn.close()

                error = "هذا الإيميل مستعمل من قبل."

            else:

                username = email.split("@")[0]

                counter = 1

                original_username = username


                while conn.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE username = ?
                    """,
                    (username,)
                ).fetchone():

                    username = (
                        original_username
                        + str(counter)
                    )

                    counter += 1


                conn.execute(
                    """
                    INSERT INTO users
                    (
                        username,
                        password,
                        phone,
                        email,
                        is_admin
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        generate_password_hash(
                            password
                        ),
                        phone,
                        email,
                        0
                    )
                )


                conn.commit()

                conn.close()

                return redirect("/login")


    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

                <div style="
                    text-align:center;
                    background:linear-gradient(
                        135deg,
                        #5b21b6,
                        #7c3aed
                    );
                    color:white;
                    padding:15px;
                    border-radius:14px;
                    margin-bottom:18px;
                ">

                    <h1>
                        Sou9na 🇹🇳
                    </h1>

                    <p>
                        إنشاء حساب جديد 👋
                    </p>

                </div>


                <h2>
                    إنشاء حساب 👤
                </h2>


                {% if error %}

                    <div class="alert">

                        {{ error }}

                    </div>

                {% endif %}


                <form method="POST">

                    <input
                        type="email"
                        name="email"
                        placeholder="📧 البريد الإلكتروني"
                        required
                    >


                    <input
                        type="password"
                        name="password"
                        placeholder="🔐 كلمة السر"
                        minlength="6"
                        required
                    >


                    <input
                        type="tel"
                        name="phone"
                        placeholder="📱 رقم الهاتف"
                    >


                    <button
                        type="submit"
                        style="width:100%;"
                    >

                        🚀 إنشاء الحساب

                    </button>

                </form>


                <br>


                <a href="/login">

                    عندك حساب؟
                    تسجيل الدخول

                </a>

            </div>

        </div>

        """,

        error=error

    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
@app.route("/add", methods=["GET", "POST"])
def add():

    if not session.get("user_id"):
        return redirect("/login")

    error = ""

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()

        images = request.files.getlist("images")
        filenames = []

        if not title or not price or not category or not location:

            error = "لازم تعمر الاسم والسعر والتصنيف والمكان."

        else:

            for image in images[:5]:

                if image and image.filename:

                    filename = secure_filename(
                        str(time.time_ns()) + "_" + image.filename
                    )

                    image.save(
                        os.path.join(
                            UPLOAD_FOLDER,
                            filename
                        )
                    )

                    filenames.append(filename)

            image_names = "|".join(filenames)

            conn = get_db()

            conn.execute(
                """
                INSERT INTO ads
                (
                    title,
                    description,
                    price,
                    category,
                    location,
                    image,
                    user_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    description,
                    price,
                    category,
                    location,
                    image_names,
                    session["user_id"]
                )
            )

            conn.commit()
            conn.close()

            return redirect("/")

    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

                <h2>
                    📢 نشر منتج
                </h2>

                {% if error %}

                    <div class="alert">
                        {{ error }}
                    </div>

                {% endif %}

                <form
                    method="POST"
                    enctype="multipart/form-data"
                >

                    <input
                        type="text"
                        name="title"
                        placeholder="📦 اسم المنتج"
                        required
                    >

                    <textarea
                        name="description"
                        placeholder="📝 وصف المنتج"
                        rows="5"
                    ></textarea>

                    <input
                        type="text"
                        name="price"
                        placeholder="💰 السعر بالدينار"
                        required
                    >

                    <select
                        name="category"
                        required
                    >

                        <option value="">
                            📂 اختر التصنيف
                        </option>

                        {% for icon, c in categories %}

                            <option value="{{ c }}">
                                {{ icon }} {{ c }}
                            </option>

                        {% endfor %}

                    </select>

                    <input
                        type="text"
                        name="location"
                        placeholder="📍 المكان"
                        required
                    >

                    <label>
                        📷 صور المنتج (حتى 5 صور)
                    </label>

                    <input
                        type="file"
                        name="images"
                        accept="image/*"
                        multiple
                    >

                    <button type="submit">
                        🚀 نشر المنتج
                    </button>

                </form>

            </div>

        </div>

        """,

        error=error,
        categories=CATEGORIES
    )
@app.route("/ad/<int:ad_id>")
def ad_details(ad_id):

    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db()

    ad = conn.execute(
        """
        SELECT
            ads.*,
            users.username,
            users.phone,
            users.email
        FROM ads
        LEFT JOIN users
        ON ads.user_id = users.id
        WHERE ads.id = ?
        """,
        (ad_id,)
    ).fetchone()

    conn.close()

    if not ad:

        return render_template_string(
            STYLE + """

            <div class="container">

                <div class="form-box">

                    <h2>
                        الإعلان غير موجود ❌
                    </h2>

                    <a
                        class="btn"
                        href="/"
                    >
                        🏠 العودة للرئيسية
                    </a>

                </div>

            </div>

            """
        ), 404

    images = []

    if ad["image"]:

        images = [
            x
            for x in ad["image"].split("|")
            if x
        ]

    return render_template_string(

        STYLE + """

        <nav>

            <div class="nav-container">

                <div class="logo">
                    Sou9na 🇹🇳
                </div>

                <div>

                    <a href="/">
                        🏠 الرئيسية
                    </a>

                    <a href="/profile">
                        👤 حسابي
                    </a>

                </div>

            </div>

        </nav>

        <div class="container">

            <div class="detail">

                {% if images %}

                    <img
                        src="/static/uploads/{{ images[0] }}"
                    >

                {% else %}

                    <div style="
                        width:100%;
                        height:250px;
                        background:#eee;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        border-radius:12px;
                        font-size:50px;
                    ">
                        📷
                    </div>

                {% endif %}

                <h1>
                    {{ ad['title'] }}
                </h1>

                <div class="price">

                    💰
                    {{ ad['price'] }}
                    د.ت

                </div>

                <hr>

                <h3>
                    📝 وصف المنتج
                </h3>

                <p>
                    {{ ad['description'] or 'لا يوجد وصف للمنتج.' }}
                </p>

                <hr>

                <p>
                    📂 التصنيف:
                    <b>
                        {{ ad['category'] }}
                    </b>
                </p>

                <p>
                    📍 المكان:
                    <b>
                        {{ ad['location'] }}
                    </b>
                </p>

                <p>
                    👤 البائع:
                    <b>
                        {{ ad['username'] or 'غير معروف' }}
                    </b>
                </p>

                {% if ad['phone'] %}

                    <p>
                        📱 الهاتف:
                        <a href="tel:{{ ad['phone'] }}">
                            {{ ad['phone'] }}
                        </a>
                    </p>

                    <a
                        class="btn"
                        href="tel:{{ ad['phone'] }}"
                    >
                        📞 اتصل بالبائع
                    </a>

                {% endif %}

                {% if ad['email'] %}

                    <p>
                        📧 البريد:
                        <a href="mailto:{{ ad['email'] }}">
                            {{ ad['email'] }}
                        </a>
                    </p>

                {% endif %}

                <br>

                {% if session.get("user_id") == ad["user_id"]
                   or session.get("is_admin") %}

                    <a
                        class="btn btn-danger"
                        href="/delete/{{ ad['id'] }}"
                        onclick="
                            return confirm(
                                'متأكد تحب تحذف الإعلان؟'
                            );
                        "
                    >
                        🗑️ حذف الإعلان
                    </a>

                {% endif %}

            </div>

        </div>

        """,

        ad=ad,
        images=images
    )


@app.route("/delete/<int:ad_id>")
def delete_ad(ad_id):

    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db()

    ad = conn.execute(
        """
        SELECT *
        FROM ads
        WHERE id = ?
        """,
        (ad_id,)
    ).fetchone()

    if ad:

        allowed = (
            ad["user_id"] == session["user_id"]
            or session.get("is_admin")
        )

        if allowed:

            if ad["image"]:

                for filename in ad["image"].split("|"):

                    path = os.path.join(
                        UPLOAD_FOLDER,
                        filename
                    )

                    if os.path.exists(path):

                        try:
                            os.remove(path)
                        except OSError:
                            pass

            conn.execute(
                """
                DELETE FROM ads
                WHERE id = ?
                """,
                (ad_id,)
            )

            conn.commit()

    conn.close()

    return redirect("/")
@app.route("/profile")
def profile():

    if not session.get("user_id"):
        return redirect("/login")

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    ads = conn.execute(
        """
        SELECT *
        FROM ads
        WHERE user_id = ?
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

                <div class="welcome">

                    👋 مرحباً

                    <b>
                        {{ user['username'] }}
                    </b>

                </div>

                <h2>
                    👤 حسابي
                </h2>

                <p>
                    👤 المستخدم:
                    <b>
                        {{ user['username'] }}
                    </b>
                </p>

                <p>
                    📧 الإيميل:
                    <b>
                        {{ user['email'] or 'غير موجود' }}
                    </b>
                </p>

                <p>
                    📱 الهاتف:
                    <b>
                        {{ user['phone'] or 'غير موجود' }}
                    </b>
                </p>

                <hr>

                <h3>
                    📢 إعلاناتي
                </h3>

                {% for ad in ads %}

                    <div class="admin-card">

                        <h3>
                            {{ ad['title'] }}
                        </h3>

                        <p class="price">
                            💰
                            {{ ad['price'] }}
                            د.ت
                        </p>

                        <a
                            class="btn"
                            href="/ad/{{ ad['id'] }}"
                        >
                            👁️ مشاهدة
                        </a>

                        <a
                            class="btn btn-danger"
                            href="/delete/{{ ad['id'] }}"
                            onclick="
                                return confirm(
                                    'حذف الإعلان؟'
                                );
                            "
                        >
                            🗑️ حذف
                        </a>

                    </div>

                {% else %}

                    <p>
                        ما عندك حتى إعلان.
                    </p>

                {% endfor %}

                <br>

                <a
                    class="btn"
                    href="/add"
                >
                    📢 نشر إعلان
                </a>

                <a
                    class="btn btn-danger"
                    href="/logout"
                >
                    🚪 خروج
                </a>

            </div>

        </div>

        """,

        user=user,
        ads=ads
    )


@app.route("/admin")
def admin():

    if not session.get("is_admin"):

        return """
        <h2 style="
            text-align:center;
            margin-top:50px;
        ">
            ممنوع الدخول ❌
        </h2>
        """, 403

    conn = get_db()

    ads = conn.execute(
        """
        SELECT
            ads.*,
            users.username,
            users.email,
            users.phone
        FROM ads
        LEFT JOIN users
        ON ads.user_id = users.id
        ORDER BY ads.id DESC
        """
    ).fetchall()

    users = conn.execute(
        """
        SELECT *
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    total_ads = conn.execute(
        "SELECT COUNT(*) FROM ads"
    ).fetchone()[0]

    total_users = conn.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    conn.close()

    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="admin-header">

                <h1>
                    🛡️ لوحة التحكم
                </h1>

                <p>
                    إدارة Sou9na 🇹🇳
                </p>

                <p>
                    👑 الأدمن:
                    <b>
                        {{ session.get('username') }}
                    </b>
                </p>

            </div>

            <div class="admin-stats">

                <div class="stat">

                    <div style="font-size:30px;">
                        📢
                    </div>

                    <div class="stat-number">
                        {{ total_ads }}
                    </div>

                    <div>
                        الإعلانات
                    </div>

                </div>

                <div class="stat">

                    <div style="font-size:30px;">
                        👥
                    </div>

                    <div class="stat-number">
                        {{ total_users }}
                    </div>

                    <div>
                        المستخدمين
                    </div>

                </div>

            </div>

            <h2>
                📂 التصنيفات
            </h2>

            <div class="category-box">

                {% for icon, c in categories %}

                    <div class="category-item">

                        <span style="font-size:25px;">
                            {{ icon }}
                        </span>

                        <br>

                        {{ c }}

                    </div>

                {% endfor %}

            </div>

            <h2>
                📢 جميع الإعلانات
            </h2>

            {% for ad in ads %}

                <div class="admin-card">

                    <h3>
                        {{ ad['title'] }}
                    </h3>

                    <p class="price">
                        💰
                        {{ ad['price'] }}
                        د.ت
                    </p>

                    <p>
                        📂
                        {{ ad['category'] }}
                    </p>

                    <p>
                        📍
                        {{ ad['location'] }}
                    </p>

                    <p>
                        👤
                        {{ ad['username'] or 'غير معروف' }}
                    </p>

                    {% if ad['email'] %}

                        <p>
                            📧
                            {{ ad['email'] }}
                        </p>

                    {% endif %}

                    {% if ad['phone'] %}

                        <p>
                            📱
                            {{ ad['phone'] }}
                        </p>

                    {% endif %}

                    <div class="admin-actions">

                        <a
                            class="btn btn-blue"
                            href="/ad/{{ ad['id'] }}"
                        >
                            👁️ مشاهدة
                        </a>

                        <a
                            class="btn btn-danger"
                            href="/delete/{{ ad['id'] }}"
                            onclick="
                                return confirm(
                                    'حذف الإعلان؟'
                                );
                            "
                        >
                            🗑️ حذف
                        </a>

                    </div>

                </div>

            {% else %}

                <div class="admin-card">
                    لا توجد إعلانات.
                </div>

            {% endfor %}

            <h2>
                👥 المستخدمين
            </h2>

            {% for user in users %}

                <div class="admin-card">

                    <h3>
                        👤 {{ user['username'] }}
                    </h3>

                    <p>
                        📧
                        {{ user['email'] or 'بدون إيميل' }}
                    </p>

                    <p>
                        📱
                        {{ user['phone'] or 'بدون هاتف' }}
                    </p>

                    {% if user['is_admin'] %}

                        <b>
                            🛡️ Admin
                        </b>

                    {% else %}

                        <span>
                            👤 مستخدم
                        </span>

                    {% endif %}

                </div>

            {% endfor %}

            <br>

            <a
                class="btn"
                href="/"
            >
                🏠 الرئيسية
            </a>

            <a
                class="btn btn-danger"
                href="/logout"
            >
                🚪 خروج
            </a>

        </div>

        """,

        ads=ads,
        users=users,
        categories=CATEGORIES,
        total_ads=total_ads,
        total_users=total_users
    )


# ==============================
# تشغيل الموقع
# ==============================

init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )