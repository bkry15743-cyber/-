from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ela_allah_secret_key_2026'

users_db = {}
user_data = {}

app_state = {
    "daily_word": {
        "sura": "البقرة", 
        "total_pages": 5,
        "page_progress": {}
    },
    "chat_messages": [
        {"user": "أحمد", "msg": "أتممت الورد اليوم بحمد الله 🌿", "time": "10:30 ص"},
        {"user": "فاطمة", "msg": "أتممت الورد اليوم 📖", "time": "11:15 ص"}
    ],
    "videos": [
        {"title": "تأملات في خواتيم سورة البقرة", "url": "https://www.youtube.com/embed/dQw4w9WgXcQ"}
    ],
    "contest": {
        "active": True,
        "from_sura": "آل عمران",
        "to_sura": "النساء",
        "total_pages": 5,
        "time_limit": "45 دقيقة",
        "page_progress": {},
        "winner": None
    }
}

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إلى الله - تسجيل الدخول</title>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --gold: #d4af37; }
        * { box-sizing: border-box; font-family: 'Tajawal', sans-serif; }
        body { 
            background: linear-gradient(135deg, #0b131e 0%, #1b263b 100%); 
            min-height: 100vh; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 15px; 
            color: #ffffff; 
        }
        .login-card { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(15px); 
            border: 1px solid rgba(212, 175, 55, 0.2); 
            padding: 25px 20px; 
            border-radius: 24px; 
            width: 100%; 
            max-width: 420px; 
            text-align: center; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .image-banner {
            width: 100%;
            height: 180px;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 18px;
            border: 1px solid rgba(212, 175, 55, 0.4);
            position: relative;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
        }
        .image-banner img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: brightness(0.9) contrast(1.1);
        }
        .image-overlay {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(11, 19, 30, 0.95), transparent);
            padding: 10px;
        }
        .quote-box { font-family: 'Amiri', serif; font-size: 16px; color: #f4e285; margin: 0; }
        .quote-sub { font-size: 11px; color: #a0aec0; margin-top: 2px; }
        h1 { font-family: 'Amiri', serif; color: var(--gold); font-size: 30px; margin: 0 0 5px 0; }
        p.subtitle { font-size: 12px; color: #cbd5e0; margin-bottom: 15px; }
        .form-group { text-align: right; margin-bottom: 12px; }
        .form-group label { display: block; font-size: 12px; color: #cbd5e0; margin-bottom: 4px; }
        .input-control { width: 100%; padding: 11px 14px; background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; color: white; font-size: 14px; }
        .btn { background: linear-gradient(135deg, var(--gold), #b8860b); color: #0d1b2a; border: none; padding: 13px; border-radius: 12px; font-weight: 800; width: 100%; font-size: 15px; cursor: pointer; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>إِلَى اللَّهِ</h1>
        <p class="subtitle">تطبيق الطاعات والمنافسة الإيمانية</p>
        
        <div class="image-banner">
            <img src="https://images.unsplash.com/photo-1509114397022-ed747cca3f65?auto=format&fit=crop&w=800&q=80" alt="طريق النور">
            <div class="image-overlay">
                <div class="quote-box">"وَاهْدِنَا صِرَاطًا مُسْتَقِيمًا"</div>
                <div class="quote-sub">خطوة نحو الله تنير طريقك في الدنيا والآخرة</div>
            </div>
        </div>

        <form action="/login" method="post">
            <div class="form-group">
                <label>الاسم الكامل:</label>
                <input type="text" name="name" placeholder="أدخل اسمك" class="input-control" required>
            </div>
            <div class="form-group">
                <label>البريد الإلكتروني لحفظ البيانات:</label>
                <input type="email" name="email" placeholder="example@mail.com" class="input-control" required>
            </div>
            <div class="form-group">
                <label>كلمة المرور:</label>
                <input type="password" name="password" placeholder="••••••••" class="input-control" required>
            </div>
            <button class="btn" type="submit">دخول / إنشاء حساب</button>
        </form>
    </div>
</body>
</html>
"""

MAIN_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تطبيق إلى الله</title>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #1b4332; --gold: #d4af37; --bg: #f4f7f6; }
        * { box-sizing: border-box; font-family: 'Tajawal', sans-serif; }
        body { background-color: var(--bg); margin: 0; padding: 15px; color: #2d3142; display: flex; justify-content: center; }
        .app-container { width: 100%; max-width: 500px; }
        .header { background: linear-gradient(135deg, #0d1b2a, #1b4332); color: white; padding: 20px; border-radius: 20px; text-align: center; margin-bottom: 20px; position: relative; }
        .header h1 { font-family: 'Amiri', serif; margin: 0; font-size: 28px; color: var(--gold); }
        .logout-btn { position: absolute; left: 15px; top: 15px; background: rgba(255,255,255,0.15); color: white; padding: 6px 12px; border-radius: 8px; text-decoration: none; font-size: 12px; }
        .tabs { display: flex; gap: 6px; margin-bottom: 15px; overflow-x: auto; }
        .tab-btn { background: #e2e8f0; border: none; padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 12px; cursor: pointer; flex: 1; white-space: nowrap; }
        .tab-btn.active { background: var(--primary); color: white; }
        .card { background: white; border-radius: 18px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
        .btn { background: #2d6a4f; color: white; border: none; padding: 8px 12px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 12px; }
        .btn-warning { background: #e67e22; }
        .btn-alarm { background: #8e44ad; }
        .chat-box { background: #f8f9fa; border-radius: 12px; padding: 10px; height: 140px; overflow-y: auto; margin-top: 10px; }
        .chat-item { background: white; padding: 8px 12px; border-radius: 10px; margin-bottom: 6px; display: flex; justify-content: space-between; font-size: 13px; border-right: 3px solid #2d6a4f; }
        .alarm-item { background: #f8f0fb; border-right: 4px solid #8e44ad; padding: 10px; border-radius: 8px; margin-bottom: 8px; display: flex; justify-content: space-between; }
        .input-control { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: 'Tajawal'; margin-bottom: 8px; }
        
        .page-list { margin-top: 12px; }
        .page-item { display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; padding: 8px 12px; border-radius: 10px; margin-bottom: 6px; border: 1px solid #edf2f7; }
        .page-done { background: #f0fff4; border-color: #c6f6d5; }
        .winner-box { background: linear-gradient(135deg, #fff9db, #fff3bf); border: 2px solid #f59f00; border-radius: 14px; padding: 15px; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <a href="/logout" class="logout-btn">خروج</a>
            <h1>إِلَى اللَّهِ</h1>
            <p>مرحباً بك يا <b>{{ user_name }}</b> 🌿</p>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('word')">📖 ورد اليوم</button>
            <button class="tab-btn" onclick="showTab('tafaqah')">📚 تفقه</button>
            <button class="tab-btn" onclick="showTab('contest')">🏆 تسابقوا</button>
            <button class="tab-btn" onclick="showTab('alarms')">🔔 المنبه</button>
            {% if is_admin %}
                <button class="tab-btn" onclick="showTab('admin')" style="background:#2c3e50; color:white;">⚙️ التحكم</button>
            {% endif %}
        </div>

        <!-- 1. ورد اليوم -->
        <div id="word" class="tab-content">
            <div class="card">
                <h3>📖 الورد اليومي المحدد</h3>
                <p><b>السورة:</b> {{ state.daily_word.sura }} | <b>المطلوب:</b> {{ state.daily_word.total_pages }} صفحات</p>
                
                <h4 style="margin-top:12px; margin-bottom:8px; font-size:13px; color:#1b4332;">📄 متابعة القراءة صفحة بصفحة:</h4>
                <div class="page-list">
                    {% for p in range(1, state.daily_word.total_pages + 1) %}
                        {% set p_str = p|string %}
                        {% set is_done = p_str in state.daily_word.page_progress %}
                        <div class="page-item {% if is_done %}page-done{% endif %}">
                            <div>
                                <b>صفحة {{ p }}</b>
                                {% if is_done %}
                                    <span style="font-size:11px; color:#276749; margin-right:6px;">
                                        (قرأها: <b>{{ state.daily_word.page_progress[p_str].user }}</b> - {{ state.daily_word.page_progress[p_str].time }})
                                    </span>
                                {% endif %}
                            </div>
                            <div>
                                {% if is_done %}
                                    <span style="font-size:11px; color:#38a169;">✔ أُتِمَّت</span>
                                {% else %}
                                    <form action="/read_page" method="post" style="display:inline;">
                                        <input type="hidden" name="page_num" value="{{ p }}">
                                        <button class="btn" type="submit">إتمام الصفحة</button>
                                    </form>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </div>

                <form action="/read" method="post" style="background:#f8f9fa; padding:10px; border-radius:12px; margin-top:12px;">
                    <label style="font-size:11px; font-weight:bold; color:#4a5568;">تأكيد القراءة للورد كاملاً في المحادثة:</label>
                    <input type="text" name="custom_name" value="{{ user_name }}" class="input-control" style="margin-top:4px;" required>
                    <button class="btn" style="width:100%; font-size:13px; padding:10px;" type="submit">✔ إعلان إتمام الورد كاملاً</button>
                </form>

                <h4 style="margin-top:12px; font-size:12px; color:#666;">💬 سجل المكتملين للورد:</h4>
                <div class="chat-box">
                    {% for item in state.chat_messages %}
                        <div class="chat-item">
                            <div><b>{{ item.user }}</b>: {{ item.msg }}</div>
                            <div style="font-size: 10px; color: #aaa;">{{ item.time }}</div>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- 2. تفقه -->
        <div id="tafaqah" class="tab-content" style="display:none;">
            <div class="card">
                <h3>📚 نافذة تفقه</h3>
                {% for video in state.videos %}
                    <div style="margin-bottom: 15px;">
                        <div style="font-weight: 700; font-size: 13px; margin-bottom: 5px;">🎥 {{ video.title }}</div>
                        <iframe style="width:100%; height:200px; border:0; border-radius:10px;" src="{{ video.url }}" allowfullscreen></iframe>
                    </div>
                {% endfor %}
            </div>
        </div>

        <!-- 3. تسابقوا -->
        <div id="contest" class="tab-content" style="display:none;">
            <div class="card">
                <h3>🏆 تسابقوا إلى الله</h3>
                <p><b>النطاق:</b> من سورة {{ state.contest.from_sura }} إلى {{ state.contest.to_sura }}</p>
                <p style="color:#e53e3e; font-size:13px;"><b>الزمن المحدد للتحدي:</b> {{ state.contest.time_limit }}</p>
                
                {% if state.contest.winner %}
                    <div class="winner-box">
                        <h3 style="margin:0 0 5px 0; color:#d97706;">🥇 الفائز بالمركز الأول: {{ state.contest.winner }}</h3>
                        <p style="font-family:'Amiri'; font-size:16px; margin:5px 0; color:#92400e;">
                            "إِنَّ الَّذِينَ يَتْلُونَ كِتَابَ اللَّهِ وَأَقَامُوا الصَّلَاةَ وَأَنفَقُوا مِمَّا رَزَقْنَاهُمْ سِرًّا وَعَلَانِيَةً يَرْجُونَ تِجَارَةً لَّن تَبُورَ"
                        </p>
                        <small style="color:#b45309;">هنيئاً لك الأجر العظيم والمجازاة من الله تعالى بكتابه الكريم!</small>
                    </div>
                {% endif %}

                <h4 style="margin-top:15px; margin-bottom:8px; font-size:14px; color:#1b4332;">📄 لستة صفحات التحدي:</h4>
                <div class="page-list">
                    {% for p in range(1, state.contest.total_pages + 1) %}
                        {% set p_str = p|string %}
                        {% set is_done = p_str in state.contest.page_progress %}
                        <div class="page-item {% if is_done %}page-done{% endif %}">
                            <div>
                                <b>الصفحة {{ p }}</b>
                                {% if is_done %}
                                    <span style="font-size:11px; color:#276749; margin-right:6px;">
                                        (أتمها: <b>{{ state.contest.page_progress[p_str].user }}</b>)
                                    </span>
                                {% endif %}
                            </div>
                            <div>
                                {% if is_done %}
                                    <span style="font-size:11px; color:#38a169;">✔ مكتملة</span>
                                {% else %}
                                    <form action="/complete_page" method="post" style="display:inline;">
                                        <input type="hidden" name="page_num" value="{{ p }}">
                                        <button class="btn btn-warning" type="submit">إتمام الصفحة</button>
                                    </form>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- 4. المنبه -->
        <div id="alarms" class="tab-content" style="display:none;">
            <div class="card">
                <h3>🔔 منبه الطاعات</h3>
                {% for alarm in alarms %}
                    <div class="alarm-item">
                        <div><b>{{ alarm.title }}</b></div>
                        <div style="color: #8e44ad; font-weight:bold;">🕒 {{ alarm.time }}</div>
                    </div>
                {% endfor %}
                <form action="/add_alarm" method="post" style="margin-top:10px;">
                    <select name="type" class="input-control">
                        <option value="تذكير بالورد اليومي">📖 تذكير بالورد اليومي</option>
                        <option value="تذكير بموعد المسابقة">🏆 تذكير بموعد المسابقة</option>
                    </select>
                    <input type="time" name="time" class="input-control" required>
                    <button class="btn btn-alarm" style="width:100%; margin-top:5px; padding:10px;" type="submit">➕ إضافة منبه</button>
                </form>
            </div>
        </div>

        <!-- 5. لوحة التحكم -->
        {% if is_admin %}
        <div id="admin" class="tab-content" style="display:none;">
            <div class="card">
                <h3>⚙️ لوحة تحكم المالك</h3>
                <form action="/admin/update_word" method="post" style="margin-bottom:10px;">
                    <input type="text" name="sura" placeholder="اسم السورة" class="input-control" required>
                    <input type="number" name="pages" placeholder="عدد الصفحات" class="input-control" required>
                    <button class="btn" style="width:100%; padding:10px;" type="submit">تحديث الورد</button>
                </form>
            </div>
        </div>
        {% endif %}
    </div>

    <script>
        function showTab(tabId) {
            let contents = document.getElementsByClassName('tab-content');
            for(let i = 0; i < contents.length; i++) { contents[i].style.display = 'none'; }
            let btns = document.getElementsByClassName('tab-btn');
            for(let i = 0; i < btns.length; i++) { btns[i].classList.remove('active'); }
            document.getElementById(tabId).style.display = 'block';
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    if 'email' not in session:
        return redirect('/login')
    
    email = session['email']
    user_name = session.get('name', 'المستخدم')
    alarms = user_data.get(email, {}).get('alarms', [])
    is_admin = (email == "admin@allah.com")
    
    return render_template_string(
        MAIN_TEMPLATE, 
        user_name=user_name, 
        alarms=alarms, 
        state=app_state, 
        is_admin=is_admin
    )

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        users_db[email] = {'password': password, 'name': name}
        if email not in user_data:
            user_data[email] = {'alarms': []}
        
        session['email'] = email
        session['name'] = name
        return redirect('/')
        
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/read_page', methods=['POST'])
def read_page():
    page_num = request.form.get('page_num')
    user_name = session.get('name', 'مستخدم')
    
    app_state['daily_word']['page_progress'][str(page_num)] = {
        "user": user_name,
        "time": datetime.now().strftime("%I:%M %p")
    }
    return redirect('/')

@app.route('/read', methods=['POST'])
def mark_read():
    custom_name = request.form.get('custom_name', '').strip()
    if not custom_name:
        custom_name = session.get('name', 'مستخدم')
        
    app_state['chat_messages'].insert(0, {
        "user": custom_name, 
        "msg": "أتممت الورد اليوم كاملًا بحمد الله 🌿", 
        "time": datetime.now().strftime("%I:%M %p")
    })
    return redirect('/')

@app.route('/complete_page', methods=['POST'])
def complete_page():
    page_num = request.form.get('page_num')
    user_name = session.get('name', 'مستخدم')
    
    app_state['contest']['page_progress'][str(page_num)] = {
        "user": user_name,
        "time": datetime.now().strftime("%I:%M %p")
    }
    
    completed_count = len(app_state['contest']['page_progress'])
    if completed_count == app_state['contest']['total_pages'] and not app_state['contest']['winner']:
        app_state['contest']['winner'] = user_name

    return redirect('/')

@app.route('/add_alarm', methods=['POST'])
def add_alarm():
    if 'email' in session:
        email = session['email']
        alarm_type = request.form.get('type')
        alarm_time = request.form.get('time')
        user_data[email]['alarms'].append({
            "title": alarm_type, 
            "time": alarm_time
        })
    return redirect('/')

@app.route('/admin/update_word', methods=['POST'])
def update_word():
    if session.get('email') == "admin@allah.com":
        app_state['daily_word']['sura'] = request.form.get('sura')
        app_state['daily_word']['total_pages'] = int(request.form.get('pages', 5))
        app_state['daily_word']['page_progress'] = {}
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
