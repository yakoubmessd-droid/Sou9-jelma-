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
        ("admin",)
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
                "admin",
                generate_password_hash("1234"),
                "",
                "admin@sou9jilma.tn",
                1
            )
        )

    else:

        old_password = admin["password"]

        if old_password == "1234":

            conn.execute(
                """
                UPDATE users
                SET password = ?,
                    email = ?
                WHERE username = ?
                """,
                (
                    generate_password_hash("1234"),
                    "admin@sou9jilma.tn",
                    "admin"
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

html {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
}

body {
    width: 100%;
    min-height: 100vh;
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    color: #222;
    overflow-x: hidden;
}

/* NAVBAR */

nav {
    width: 100%;
    min-height: 60px;
    background: #075e54;
    color: white;
    padding: 12px 10px;
}

.nav-container {
    width: 100%;
    max-width: none;
    margin: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 21px;
    font-weight: bold;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 3px;
}

/* MAIN */

.container {
    width: 100%;
    max-width: none;
    min-height: calc(100vh - 60px);
    margin: 0;
    padding: 10px;
}

/* HERO */

.hero {
    width: 100%;
    background: white;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.hero h1 {
    color: #075e54;
    margin-top: 0;
}

/* SEARCH */

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
    border: 1px solid #ddd;
    border-radius: 10px;
    margin-bottom: 10px;
    font-size: 16px;
}

/* BUTTON */

button,
.btn {
    background: #075e54;
    color: white;
    border: none;
    padding: 13px 18px;
    border-radius: 10px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
}

/* PRODUCTS */

.grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}

.card {
    width: 100%;
    background: white;
    border-radius: 13px;
    overflow: hidden;
    box-shadow: 0 2px 8px #00000015;
}

.card img {
    width: 100%;
    height: 145px;
    object-fit: cover;
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
    color: #075e54;
    font-size: 17px;
    font-weight: bold;
}

.category {
    color: #777;
    font-size: 13px;
}

/* FORM */

.form-box {
    width: 100%;
    max-width: 600px;
    margin: 10px auto;
    background: white;
    padding: 18px;
    border-radius: 15px;
}

/* DETAILS */

.detail {
    width: 100%;
    background: white;
    padding: 15px;
    border-radius: 15px;
}

.detail img {
    width: 100%;
    max-height: 450px;
    object-fit: contain;
    border-radius: 12px;
}

/* ADMIN */

.admin-header {
    width: 100%;
    background: linear-gradient(135deg, #075e54, #0a806f);
    color: white;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.admin-stats {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
}

.stat {
    background: white;
    border-radius: 13px;
    padding: 15px;
    text-align: center;
}

.category-box {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
}

.category-item {
    background: white;
    border-radius: 13px;
    padding: 14px 8px;
    text-align: center;
}

footer {
    width: 100%;
    text-align: center;
    padding: 25px 10px;
    color: #777;
}

/* PHONE */

@media (max-width: 600px) {

    html,
    body {
        width: 100vw !important;
        min-width: 100vw !important;
        max-width: 100vw !important;
        min-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .container {
        width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 8px !important;
    }

    .grid {
        width: 100% !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    .card {
        width: 100% !important;
    }

    .nav-container {
        width: 100% !important;
    }
}

</style>
"""
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
            error = "لازم تعمّر الاسم والسعر والتصنيف والمكان."

        else:

            for image in images[:5]:

                if image and image.filename:

                    filename = secure_filename(
                        str(time.time_ns()) +
                        "_" +
                        image.filename
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

                    <label>📷 صور المنتج (حتى 5 صور)</label>

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


@app.route("/")
def home():

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

        params.extend(
            [
                word,
                word,
                word
            ]
        )

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
                    Sou9 Jilma 🇹🇳
                </div>

                <div>

                    <a href="/">
                        🏠 الرئيسية
                    </a>

                    {% if session.get('user_id') %}

                        <a href="/add">
                            📢 نشر
                        </a>

                        <a href="/logout">
                            خروج
                        </a>

                    {% else %}

                        <a href="/login">
                            دخول
                        </a>

                        <a href="/register">
                            حساب
                        </a>

                    {% endif %}

                    {% if session.get('is_admin') %}

                        <a href="/admin">
                            🛡️ Admin
                        </a>

                    {% endif %}

                </div>

            </div>

        </nav>


        <div class="container">

            <div class="hero">

                <h1>
                    سوق جلمة 🛒
                </h1>

                <p>
                    بيع وشراء داخل جلمة 🇹🇳
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

                                {{ icon }} {{ c }}

                            </option>

                        {% endfor %}

                    </select>

                    <button>
                        🔍 بحث
                    </button>

                </form>

            </div>


            <div class="grid">

                {% for ad in ads %}

                    <div class="card">

                        {% if ad['image'] %}

                            <img
                                src="/static/uploads/{{ ad['image'].split('|')[0] }}"
                            >

                        {% else %}

                            <div style="
                                height:180px;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                background:#ddd;
                            ">

                                📷 بدون صورة

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

                            <a
                                class="btn"
                                href="/ad/{{ ad['id'] }}"
                            >

                                👁️ التفاصيل

                            </a>

                        </div>

                    </div>

                {% else %}

                    <p>
                        ما فماش إعلانات حاليًا.
                    </p>

                {% endfor %}

            </div>

        </div>


        <footer>

            Sou9 Jilma © 2026 🇹🇳

        </footer>

        """,

        ads=ads,

        search=search,

        category=category,

        categories=CATEGORIES

    )


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    error = ""

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]

        phone = request.form[
            "phone"
        ].strip()

        if not email or not password:

            error = """
                اكتب الإيميل وكلمة السر.
            """

        elif "@" not in email:

            error = """
                الإيميل غير صحيح.
            """

        elif len(password) < 6:

            error = """
                كلمة السر لازم تكون
                6 أحرف على الأقل.
            """

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

                error = """
                    هذا الإيميل مستعمل من قبل.
                """

            else:

                username = (
                    email
                    .split("@")[0]
                )

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
                        email
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        username,
                        generate_password_hash(
                            password
                        ),
                        phone,
                        email
                    )
                )

                conn.commit()

                conn.close()

                return redirect("/login")


    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

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

                    <button>
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


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    error = ""

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip().lower()

        password = request.form[
            "password"
        ]

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        valid = False

        if user:

            try:

                valid = check_password_hash(
                    user["password"],
                    password
                )

            except ValueError:

                valid = (
                    user["password"]
                    == password
                )


        if valid:

            session["user_id"] = \
                user["id"]

            session["username"] = \
                user["username"]

            session["is_admin"] = \
                user["is_admin"]

            return redirect("/")

        error = """
            الإيميل أو كلمة السر غلط.
        """


    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

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
                        type="email"
                        name="email"
                        placeholder="📧 البريد الإلكتروني"
                        required
                    >

                    <input
                        type="password"
                        name="password"
                        placeholder="🔐 كلمة السر"
                        required
                    >

                    <button>
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


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")@app.route("/ad/<int:ad_id>")
def ad_details(ad_id):

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

        return """

        <h2 style="text-align:center">
            الإعلان غير موجود ❌
        </h2>

        <p style="text-align:center">
            <a href="/">
                العودة للرئيسية
            </a>
        </p>

        """, 404


    return render_template_string(

        STYLE + """

        <nav>

            <div class="nav-container">

                <div class="logo">
                    Sou9 Jilma 🇹🇳
                </div>

                <div>

                    <a href="/">
                        🏠 الرئيسية
                    </a>

                </div>

            </div>

        </nav>


        <div class="container">

            <div class="detail">

                {% if ad['image'] %}

                    <img
                        src="/static/uploads/{{ ad['image'].split('|')[0] }}"
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


                <p>

                    {{ ad['description'] }}

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
                        {{ ad['username'] }}
                    </b>
                </p>


                {% if ad['phone'] %}

                    <p>

                        📱 الهاتف:

                        <a
                            href="tel:{{ ad['phone'] }}"
                        >
                            {{ ad['phone'] }}
                        </a>

                    </p>

                {% endif %}


                {% if ad['email'] %}

                    <p>

                        📧 البريد:

                        <a
                            href="mailto:{{ ad['email'] }}"
                        >
                            {{ ad['email'] }}
                        </a>

                    </p>

                {% endif %}


                <br>


                {% if ad['phone'] %}

                    <a
                        class="btn"
                        href="tel:{{ ad['phone'] }}"
                    >
                        📞 اتصل بالبائع
                    </a>

                {% endif %}


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

        """

        ,

        ad=ad

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

            ad["user_id"]
            == session["user_id"]

            or

            session.get("is_admin")

        )


        if allowed:

            if ad["image"]:

                path = os.path.join(
                    UPLOAD_FOLDER,
                    ad["image"]
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
        """,
        (session["user_id"],)
    ).fetchall()


    conn.close()


    return render_template_string(

        STYLE + """

        <div class="container">

            <div class="form-box">

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
                        {{ user['email'] }}
                    </b>
                </p>

                <p>
                    📱 الهاتف:
                    <b>
                        {{ user['phone']
                           or
                           'غير موجود' }}
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

        <h2 style="text-align:center">
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
                    إدارة Sou9 Jilma
                </p>

            </div>


            <div class="admin-stats">

                <div class="stat">

                    <div class="stat-icon">
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

                    <div class="stat-icon">
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

                        <span
                            class="category-icon"
                        >
                            {{ icon }}
                        </span>

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
                        {{ ad['username'] }}
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
                        👤
                        {{ user['username'] }}
                    </h3>

                    <p>
                        📧
                        {{ user['email']
                           or
                           'بدون إيميل' }}
                    </p>

                    <p>
                        📱
                        {{ user['phone']
                           or
                           'بدون هاتف' }}
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

        </div>

        """,

        ads=ads,

        users=users,

        categories=CATEGORIES,

        total_ads=total_ads,

        total_users=total_users

    )# ==============================
# تشغيل الموقع
# ==============================

init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )