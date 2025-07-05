import telebot, json, random, os
from telebot import types

TOKEN = "8111008090:AAFv16CHnoYBTDt8vUZIXbOimVb0OZmAO7o"
ADMIN_ID = 7164117238
bot = telebot.TeleBot(TOKEN)

if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {
            "name": message.from_user.first_name,
            "gender": None,
            "coins": 5,
            "chat": None,
            "chat3": [],
            "blocked": [],
            "friends": [],
            "rating": 0,
            "votes": 0,
            "reported": 0
        }
        save_users(users)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🧑‍💻 تنظیم جنسیت", "🎲 تاس روزانه")
        markup.row("💬 چت تصادفی", "👥 چت هدفمند", "👪 چت سه‌نفره")
        markup.row("📜 پروفایل", "📛 ریپورت", "🧨 حذف حساب")
        markup.row("📊 رتبه‌بندی", "📅 جایزه هفتگی", "🧑‍🤝‍🧑 لیست دوستان")
        bot.send_message(message.chat.id, "🎉 به ربات چت ناشناس خوش اومدی!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "✅ خوش برگشتی!")

@bot.message_handler(func=lambda m: True)
def main(message):
    users = load_users()
    uid = str(message.from_user.id)

    if uid not in users:
        bot.send_message(message.chat.id, "❗️ لطفا /start رو بزن اول.")
        return

    if message.text == "🧑‍💻 تنظیم جنسیت":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("دختر 🚺", callback_data="gender_girl"))
        markup.add(types.InlineKeyboardButton("پسر 🚹", callback_data="gender_boy"))
        bot.send_message(message.chat.id, "جنسیتتو انتخاب کن:", reply_markup=markup)

    elif message.text == "🎲 تاس روزانه":
        num = random.randint(1, 6)
        users[uid]['coins'] += num
        save_users(users)
        bot.send_message(uid, f"🎲 عدد تاس: {num}\n💰 سکه‌های جدید: {users[uid]['coins']}")

    elif message.text == "📜 پروفایل":
        u = users[uid]
        gender = "🚺 دختر" if u['gender'] == "girl" else "🚹 پسر" if u['gender'] == "boy" else "❓ مشخص نشده"
        rating = round(u['rating'] / u['votes'], 2) if u['votes'] else 0
        bot.send_message(uid, f"👤 نام: {u['name']}\n🆔 آیدی: {uid}\n⚧️ جنسیت: {gender}\n💰 سکه: {u['coins']}\n⭐️ امتیاز: {rating} ({u['votes']} رأی)")

    elif message.text == "💬 چت تصادفی":
        users[uid]['chat'] = None
        save_users(users)
        for other_id, u in users.items():
            if other_id != uid and not u['chat'] and u['gender'] and other_id not in users[uid]['blocked']:
                users[uid]['chat'] = other_id
                users[other_id]['chat'] = uid
                save_users(users)
                bot.send_message(uid, "✅ به یک کاربر وصل شدی! برای قطع /end رو بزن.")
                bot.send_message(other_id, "✅ به یک کاربر وصل شدی! برای قطع /end رو بزن.")
                return
        bot.send_message(uid, "❌ کاربری پیدا نشد!")

    elif message.text == "👥 چت هدفمند":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("دختر", callback_data="find_girl"))
        markup.add(types.InlineKeyboardButton("پسر", callback_data="find_boy"))
        bot.send_message(uid, "میخوای با کی چت کنی؟", reply_markup=markup)

    elif message.text == "👪 چت سه‌نفره":
        u = users[uid]
        if uid in u['chat3']:
            bot.send_message(uid, "شما در حال حاضر توی یک چت سه‌نفره هستی.")
            return
        joined = 0
        for other_id, other in users.items():
            if other_id != uid and len(other['chat3']) < 2:
                other['chat3'].append(uid)
                users[uid]['chat3'].append(other_id)
                joined += 1
                if joined == 2:
                    break
        save_users(users)
        if joined >= 2:
            for pid in users[uid]['chat3']:
                bot.send_message(pid, "✅ شما در یک چت ۳ نفره هستید! برای خروج /end رو بزن.")
            bot.send_message(uid, "✅ به چت سه‌نفره وصل شدی! برای خروج /end رو بزن.")
        else:
            bot.send_message(uid, "❌ افراد کافی برای چت سه‌نفره پیدا نشد.")

    elif message.text == "📛 ریپورت":
        if users[uid]['chat']:
            target = users[uid]['chat']
            users[target]['reported'] += 1
            bot.send_message(uid, "✅ ریپورت انجام شد.")
            save_users(users)
        else:
            bot.send_message(uid, "❌ شما با کسی چت نمی‌کنی.")

    elif message.text == "🧨 حذف حساب":
        del users[uid]
        save_users(users)
        bot.send_message(uid, "✅ حسابت حذف شد.")

    elif message.text == "📊 رتبه‌بندی":
        ranking = sorted(users.items(), key=lambda x: x[1]['rating'], reverse=True)
        msg = "🏆 ۵ کاربر برتر:\n"
        for i, (uid_, u) in enumerate(ranking[:5], 1):
            rate = round(u['rating'] / u['votes'], 2) if u['votes'] else 0
            msg += f"{i}. {u['name']} - ⭐️ {rate}\n"
        bot.send_message(uid, msg)

    elif message.text == "📅 جایزه هفتگی":
        coins = random.randint(10, 30)
        users[uid]['coins'] += coins
        save_users(users)
        bot.send_message(uid, f"🎁 جایزه هفتگی شما: {coins} سکه!")

    elif message.text == "🧑‍🤝‍🧑 لیست دوستان":
        friends = users[uid]['friends']
        if not friends:
            bot.send_message(uid, "📭 شما دوستی ندارید.")
        else:
            msg = "👥 دوستان شما:\n"
            for f in friends:
                name = users[f]['name'] if f in users else "❓"
                msg += f"• {name} ({f})\n"
            bot.send_message(uid, msg)

@bot.message_handler(commands=['end'])
def end_chat(message):
    users = load_users()
    uid = str(message.from_user.id)
    chat = users[uid].get("chat")
    if chat:
        users[uid]["chat"] = None
        users[chat]["chat"] = None
        bot.send_message(chat, "❌ چت به پایان رسید.")
        bot.send_message(uid, "❌ چت به پایان رسید.")
    if users[uid].get("chat3"):
        for pid in users[uid]['chat3']:
            if pid in users:
                users[pid]['chat3'].remove(uid)
                bot.send_message(pid, "❌ یک نفر از چت سه‌نفره خارج شد.")
        users[uid]['chat3'] = []
        bot.send_message(uid, "❌ از چت سه‌نفره خارج شدی.")
    save_users(users)

@bot.callback_query_handler(func=lambda c: True)
def callback(call):
    users = load_users()
    uid = str(call.from_user.id)

    if call.data == "gender_girl":
        users[uid]['gender'] = "girl"
        bot.send_message(uid, "✅ جنسیت شما: دختر")
    elif call.data == "gender_boy":
        users[uid]['gender'] = "boy"
        bot.send_message(uid, "✅ جنسیت شما: پسر")
    elif call.data == "find_girl":
        if users[uid]['coins'] < 2:
            bot.send_message(uid, "❌ سکه کافی نداری.")
            return
        for other_id, u in users.items():
            if u['gender'] == "girl" and not u['chat']:
                users[uid]['coins'] -= 2
                users[uid]['chat'] = other_id
                users[other_id]['chat'] = uid
                bot.send_message(uid, "✅ به یک دختر وصل شدی.")
                bot.send_message(other_id, "✅ یک کاربر پسر بهت وصل شد.")
                save_users(users)
                return
        bot.send_message(uid, "❌ کاربری پیدا نشد.")
    elif call.data == "find_boy":
        if users[uid]['coins'] < 2:
            bot.send_message(uid, "❌ سکه کافی نداری.")
            return
        for other_id, u in users.items():
            if u['gender'] == "boy" and not u['chat']:
                users[uid]['coins'] -= 2
                users[uid]['chat'] = other_id
                users[other_id]['chat'] = uid
                bot.send_message(uid, "✅ به یک پسر وصل شدی.")
                bot.send_message(other_id, "✅ یک کاربر دختر بهت وصل شد.")
                save_users(users)
                return
        bot.send_message(uid, "❌ کاربری پیدا نشد.")

    save_users(users)

print("Bot is running...")
bot.infinity_polling()
