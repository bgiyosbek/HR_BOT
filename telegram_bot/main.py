from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import re
import asyncio
import nest_asyncio
import json
import os


USER_DATA_FILE = "user_data.json"
HR_ID = 7767819355
MY_ID = 930481227


def load_user_data(user_id):
    """Load user data from the JSON file."""
    try:
        with open(USER_DATA_FILE, "r") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    return users.get(str(user_id), {})


def save_user_data(user_id, user_info):
    """Save user data to the JSON file."""
    try:
        with open(USER_DATA_FILE, "r") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    # Update user data
    users[str(user_id)] = user_info

    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Replace with your Telegram Bot Token
TOKEN = "7516315533:AAErgTz6uukUelNUeUJRu0lS1Ht0BpEyFgo"

menu_tree = {
    "main": None,
    "about_us": "main",
    "our_traditions": "about_us",
    "job_offer": "main",
    # Add more submenus as needed
}

job_requirements = {
    "Yukchi": """📢 *Yukchi* lavozimi uchun talablar:
- Moshinalarga mahsulotlarni yuklash
- Jismoniy sog‘lom va kuchli bo‘lish
- Jamoada ishlash qobiliyati
- Mas’uliyatli bo‘lish""",

    "Haydovchi": """📢 *Haydovchi* lavozimi uchun talablar:
- Transport vositalarini boshqarish huquqiga ega bo‘lish (haydovchilik guvohnomasi)
- Yo‘l qoidalarini yaxshi bilish
- Mas’uliyatli va ehtiyotkor bo‘lish""",

    "Expeditor": """📢 *Ekspeditor* lavozimi uchun talablar:
- 20 dan 40 yoshgacha erkak 
- Zararli odatlarsiz (ish vaqtida spirtli ichimlik ichish, o'ta asabiylik)
- Shu sohada 6 oy va undan ko'proq ish tajriba
- 3 kun sinov muddati (Ish haqi to'lanmaydi. Tushlik ishxona hisobidan.)
- Ish vaqti: 8 dan yukni tarqatib bo'lgunga qadar(Mavsumga qarab o'zgarib turadi)
- Mavsum: Martdan Oktabrgacha""",

    "Buxgalter": """📢 *Buxgalter* lavozimi uchun talablar:
- Moliya yoki buxgalteriya sohasida tajriba
- 1C, Excel yoki boshqa buxgalteriya dasturlarini bilish
- Hisobotlarni to‘g‘ri yuritish va tahlil qilish qobiliyati""",

    "Operator": """📢 *Operator* lavozimi uchun talablar:
- Telefon orqali mijozlar bilan muloqot qilish.
- Mijozlarga ma’lumot berish va buyurtmalarni qabul qilish.    
- Kompyuter va ofis dasturlarida ishlash qobiliyati.
- Tez va aniq javob qaytarish qobiliyati.""",

    "HR": """📢 *HR (Kadrlar bo‘limi mutaxassisi)* lavozimi uchun talablar:
- Ishga qabul qilish, ish haqi va hujjatlar bilan ishlash.
- Intervyularni tashkillashtirish va o‘tkazish.
- Xodimlarning mehnat faoliyatini nazorat qilish.
- Mehnat kodeksi va HR amaliyotlarini bilish.
- Tajriba talab qilinadi, o‘rta yoki oliy ma’lumot afzalroq.""",

    "Karachi": """📢 *Karachi* lavozimi uchun talablar:
- Mahsulotlarni joylashtirish.
- Yuklarni qabul qilish va yetkazib berishga tayyorlash.
- Jismoniy sog‘lom va bardoshli bo‘lish.
- Jamoa bilan ishlash qobiliyati.
- Tajriba shart emas, ish jarayonida o‘rgatiladi.""",

    "Ombor mudiri": """📢 *Ombor mudiri* lavozimi uchun talablar:
- Ombor hisobini yuritish va mahsulotlarni nazorat qilish.
- Buyurtmalarni qabul qilish va yetkazib berish.
- Ombor hududining tozaligini ta’minlash
- Logistika va hisob-kitob tizimlarini bilish afzalroq.
- Kamida 1-3 yil tajriba talab qilinadi.""",

    "Hamshira": """📢 *Hamshira* lavozimi uchun talablar:
- Ishchilarni tibbiy ko‘rikdan o‘tkazish.
- Shoshilinch tibbiy yordam ko‘rsatish.
- Tibbiy hujjatlarni yuritish.
- Tibbiyot bo‘yicha ma’lumotga ega bo‘lish (sertifikat yoki diplom talab qilinadi).
- Tajriba talab qilinadi.""",

    "Tozalik hodimi": """📢 *Tozalik hodimi* lavozimi uchun talablar:
-Ish joyining tozaligini ta’minlash.
-Sanitariya talablariga rioya qilish.
-Ish tajribasi talab etilmaydi, lekin afzalroq.
-Mas’uliyatli va diqqatli bo‘lish.
-O‘z vaqtida va sifatli ishlash.""",

    "Logist": """📢 *Logist* lavozimi uchun talablar:
- Mahsulotlarni tashish jarayonini rejalashtirish.
- Yuk mashinalarining marshrutlarini ishlab chiqish.
- Ombor va transport bilan bog‘liq ishlarni nazorat qilish.
- Logistika bo‘yicha tajriba talab qilinadi.
- Kompyuter va dasturlar bilan ishlash qobiliyati afzalroq.""",

    "Qorovul": """📢 *Qorovul* lavozimi uchun talablar:
- Ish joyining xavfsizligini ta’minlash.
- Hududni nazorat qilish va xavfsizlik qoidalariga rioya qilish.
- Kamera kuzatuv tizimlaridan foydalanish qobiliyati afzalroq.
- Jismoniy baquvvat va hushyor bo‘lish.
- Kechayu-kunduz ishlashga tayyor bo‘lish."""
}


job_questions = {
    "Yukchi": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Kutilgan ish maoshini darajasini ko'rsating (so'm)", ["2 500 000 - 3 500 000", "3 500 000 - 5 000 000", "+5 000 000 "]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman",["Ha", "Yo'q"])

    ],
    "Haydovchi": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Sizda qanday turdagi haydovchilik guvohnomasi bor?", ["BC", "D", "E"]),
        ("Necha yillik haydovchilik tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Kutilgan oylik maoshini darajasini ko'rsating (so'm)", ["2 500 000 - 3 500 000", "3 500 000 - 5 000 000", "+5 000 000 "]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman",["Ha", "Yo'q"])
    ],
    "Expeditor": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Kutilgan ish maoshini darajasini ko'rsating (so'm)", ["2 500 000 - 3 500 000", "3 500 000 - 5 000 000", "+5 000 000 "]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman",["Ha", "Yo'q"])
    ],
    "Buxgalter": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Rus tili bilish darajasi?",
         ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)",
          "Yomon (tushunmayman, gapira olmayman)"]),
        ("Kompyuterni bilish darajangiz", ["Umuman bilmayman", "Boshlang'ich", "O'rtacha", "Expert"]),
        ("Moliya yoki buxgalteriya sohasida tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Qaysi dasturlar bilan ishlay olasiz?", ["1C Buxgalteriya", "Excel", "Smartup","SAP", "Boshqa"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi yo‘nalishda ishlagan tajribangiz bor?", ["Kichik biznes", "Katta kompaniya", "Davlat tashkiloti"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Operator": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Rus tili bilish darajasi?",
         ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)",
          "Yomon (tushunmayman, gapira olmayman)"]),
        ("Kompyuterni bilish darajangiz", ["Umuman bilmayman", "Boshlang'ich", "O'rtacha", "Expert"]),
        ("Sizda operatorlik tajribasi bormi?", ["Ha", "Yo'q"]),
        ("Qaysi dasturlar bilan ishlay olasiz?", ["1C Buxgalteriya", "Excel", "SAP", "Smartup", "Boshqa"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi sohada operator bo‘lib ishlagansiz?", ["Call-markaz", "Omborxona", "Ishlab chiqarish", "Boshqa"]),
        ("Ish vaqti bo‘yicha qanday jadval sizga qulay?", ["kunduzi", "kechasi"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "HR": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Rus tili bilish darajasi?",
         ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)",
          "Yomon (tushunmayman, gapira olmayman)"]),
        ("Kompyuterni bilish darajangiz", ["Umuman bilmayman", "Boshlang'ich", "O'rtacha", "Expert"]),
        ("Kadrlar bo‘limida ishlagan tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Qaysi dasturlar bilan ishlay olasiz?", ["1C Buxgalteriya", "Excel", "SAP", "Smartup", "Boshqa"]),
        ("Necha yillik  ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi kompaniyalarda ishlagansiz?", ["Call-markaz", "Omborxona", "Ishlab chiqarish", "Boshqa"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Ishonch telefoni orqali murojaatlar bilan ishlash tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Karachi": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Forklift yoki yuk ko‘taruvchi texnika haydash tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qanday turdagi forklift (yuk ko'taruvchi) bilan ishlaganingiz bor?", ["Elektr", "Dizel"]),
        ("O'zbek tili bilish darajasi?", ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)", "Yomon (tushunmayman, gapira olmayman)"]),
        ("Rus tili bilish darajasi?",["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)", "Yomon (tushunmayman, gapira olmayman)"] ),
        ("Kutilgan ish maoshini darajasini ko'rsating (so'm)", ["2 500 000 - 3 500 000", "3 500 000 - 5 000 000", "+5 000 000 "]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman",["Ha", "Yo'q"])
    ],
    "Ombor mudiri": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Kompyuterni bilish darajangiz", ["Umuman bilmayman", "Boshlang'ich", "O'rtacha", "Expert"]),
        ("Ombor boshqarish tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Qaysi dasturlar bilan ishlay olasiz?", ["Excel", "Smartup","Word", "Boshqa"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi sohada ombor boshqargansiz?", ["Oziq-ovqat", "Texnika", "Qurilish ", "Boshqa"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Qaysi jarayonlarni boshqarish tajribangiz bor?", ["Tovar qabul qilish", " Ombor nazorati", "Yetkazib berish jarayoni"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Hamshira": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Rus tili bilish darajasi?",
         ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)",
          "Yomon (tushunmayman, gapira olmayman)"]),
        ("Hamshiralik guvohnomangiz bormi? ", ["Ha", "Yo'q"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi shifoxonalarda yoki klinikalarda ishlagansiz?", ["Xususiy klinikada", "Davlat klinikasida", "Ishlamaganman"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Tozalik hodimi": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldin tozalik bo‘yicha ishlaganmisiz? ", ["Ha", "Yo'q"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi joylarda tozalik ishlari bajargansiz?",
         ["Mehmonxona", "Ofis", "Zavod", "Savdo markazi", "Boshqa"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Logist": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024", None),
        ("Rus tili bilish darajasi?",
         ["Yaxshi (yaxshi tushunaman va gapiraman)", "O'rtacha (tushunaman, yomon gapiraman)",
          "Yomon (tushunmayman, gapira olmayman)"]),
        ("Logistika sohasida ishlagan tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi dasturlar bilan ishlay olasiz?", ["1C Buxgalteriya", "Excel", "Smartup", "Boshqa"]),
        ("Qaysi sohalarda logist sifatida ishlagansiz?",
         ["Transport", "Omborxona", "Yetkazib berish","Boshqa"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ],
    "Qorovul": [
        ("Jinsni tanlang", ["👨Erkak", "👩🏼Ayol"]),
        ("Pasportdagi Familiya, Ism va Sharifini kiriting", None),
        ("Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):", None),
        ("Siz turmush qurganmisiz?", ["Turmush qurgan", "Turmush qurmagan"]),
        ("Farzandlaringiz bormi?", ["Ha", "Yo'q"]),
        ("Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):", None),
        ("Telefon raqamingiz?", None),
        ("Siz talabamisiz?", ["Ha", "Yo'q"]),
        ("Sizning ta'lim darajangiz qanday?", ["O'rta", "O'rta-maxsus", "Oliy"]),
        ("Siz oldin sudlanganmisiz?", ["Ha", "Yo'q"]),
        ("Qorovul bo‘lib ishlagan tajribangiz bormi?", ["Ha", "Yo'q"]),
        ("Necha yillik ish tajribangiz bor?", ["1-3 yil", "3-5 yil", "5+ yil"]),
        ("Qaysi joylarda qorovul bo‘lib ishlagansiz?",
         ["Zavod", "Omborxona", "Savdo markazi", "Boshqa"]),
        ("Oylik maosh bo‘yicha sizning taxminiy kutilmangiz qanday?", ["3-5 mln so‘m", "5-7 mln so‘m", "7+ mln so‘m"]),
        ("Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?", None),
        ("Malumotlarimni qayta ishlashga roziman", ["Ha", "Yo'q"])
    ]
}



# Function to log user activity
def log_activity(update: Update, action: str):
    user = update.message.from_user
    user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No Username'}) - ID: {user.id}"
    print(f"{user_info} | Action: {action}")


# Function to show reply buttons on the left side of the gallery button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Started bot")
    # Reply Keyboard (Left Side Buttons)
    reply_keyboard = [
        ["🍸Biz haqimizda"],
        ["💼Bo'sh ish o'rinlari"],
        ["📩Biz bilan bog'laning"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # Send message with reply keyboard
    await update.message.reply_text("👋🏻 Assalomu alaykum, men Energy Water Distribution kompaniyasining rasmiy HR botiman!\n"
                                    "💼 Men sizga qanday yordam bera olaman?\n"
                                    "✔️ Kompaniyamiz haqida ma’lumot berish\n"
                                    "✔️ Mavjud vakansiyalar bilan tanishtirish\n"
                                    "✔️ Ishga joylashish jarayoni haqida tushuntirish\n"
                                    "✔️ Ariza topshirishda yordam berish\n"
                                    "\n"
                                    "🚀 Biz bilan o‘sish va rivojlanish imkoniyatidan foydalaning!\n"
                                    "                           \n"
                                    "--------------------------------------------------------\n"
                                    "                           \n"
                                    "👋🏻 Здравствуйте! Я — официальный HR-бот компании Energy Water.\n"
                                    "💼 Чем я могу вам помочь?\n"
                                    "✔️ Предоставить информацию о нашей компании\n"
                                    "✔️ Ознакомить вас с актуальными вакансиями\n"
                                    "✔️ Объяснить процесс трудоустройства\n"
                                    "✔️ Помочь вам подать заявку на работу\n"
                                    "\n"
                                    "🚀 Присоединяйтесь к нашей команде и развивайтесь вместе с нами!\n", reply_markup=reply_markup
                                    )

    context.user_data["last_menu"] = "main"  # Track the user's state
# Function to show submenu when "Biz haqimizda" is clicked
async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Clicked 'Biz haqimizda'")

    file_id = "AgACAgIAAxkBAWsAAXFn8jZSIUBTFSL96VStlu4bdtAg_AACsesxGx6-kUvHWpvPTAMNLwEAAwIAA3MAAzYE"
    reply_keyboard = [
        ["🌍Bizning qadriyatlarimiz!"],
        ["📍Biznig manzil"],
        ["🏠Bosh Menu","🔙 Orqaga"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(f"""
    ⚡️ENERGY WATER DISTRIBUTION MCHJ bu – mijozlarga salqin ichimliklarni etkazib berish bo’yicha xizmat ko‘rsatuvchi korxona bo’lib, o’z faoliyatini 2021-yilda 40 nafar xodim bilan boshlab bugungi kunda 200 ga yaqin xodimlar bilan safi kengayib, rivojlanib borayotgan korxona hisoblanadi.

2021-yildan buyon,  1983-yilda AQSH fuqarosi Kaleb Bredxem tomonidan ovqat hazm qilish va energiyani oshirishga yordam beradigan gazli ichimlik  sifatida yaratilgan PEPSI brend salqin ichimliklarini Toshkent shahrining barcha tumanlarida joylashgan savdo manzillariga sifatli etkazib berish bilan shug‘ullanadi. 

2021 yilda 2000 ga yaqin mijozlarga xizmat ko’rsatish bilan ish boshlab, bugungi kunda 5000 nafar mijozlarga xizmat ko’rsatib kelmoqda.""",parse_mode="Markdown", reply_markup=reply_markup)

    context.user_data["current_menu"] = "about_us"  # example


# Function to go back to the main menu
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Clicked 'Menu'")
    await start(update, context)


# Function to go  to the bizning_qadriyatlarimiz
async def our_traditions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Clicked '🌍Bizning qadriyatlarimiz!'")
    file_id = "AgACAgIAAxkBAWn192frdo67fbyqoESA36j4na7tMtKuAAI86jEbusxQS2860znEZgdHAQADAgADcwADNgQ"
    reply_keyboard = [
        ["🏠Bosh Menu","🔙 Orqaga"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text("""💡 Har qultum va har parcha bilan ko'proq tabassum hadya qilish.\n
🖇 Har qanday qarorimizni yoki harakatimizda mijozlarni rozi qilish va yuqori darajada xizmat ko'rsatish!""",parse_mode="Markdown", reply_markup=reply_markup)

    context.user_data["current_menu"] = "our_traditions"  # example


def save_last_menu(context, reply_markup):
    if "history" not in context.user_data:
        context.user_data["history"].append(reply_markup)



# Function to handle the back button dynamically
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Clicked 'Back'")
    last_menu = context.user_data.get("last_menu", "main")

    if last_menu == "about_us":

        reply_keyboard = [
            ["🌍Bizning qadriyatlarimiz!"],
            ["📍Biznig manzil"],
            ["🏠Bosh Menu","🔙 Orqaga"]
        ]                                     # Return to main menu
    elif last_menu == "our_traditions":
        reply_keyboard = [
            ["🍸Biz haqimizda"],
            ["💼Bo'sh ish o'rinlari"],
            ["📩Biz bilan bog'laning"]
            ]
        context.user_data["last_menu"] = "about_us"  # Move back one step # Return to "Biz haqimizda"
    elif last_menu == "job_offer":
        reply_keyboard = [
            ["Yukchi", "Haydovchi"],
            ["Expeditor", "Buxgalter"],
            ["Operator", "HR"],
            ["Karachi", "Ombor mudiri"],
            ["Hamshira", "Tozalik hodimi"],
            ["Logist", "Qorovul"],
            ["🏠Bosh Menu", "🔙 Orqaga"]
        ]

    else:
        reply_keyboard = [
            ["🍸Biz haqimizda"],
            ["💼Bo'sh ish o'rinlari"],
            ["📩Biz bilan bog'laning"]
        ]                                                # Default to main menu if unknown
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    # Only update the keyboard without sending a new text message
    await update.message.reply_text("Kerakli bo'limni tanlang 👇", reply_markup=reply_markup)

async def send_actual_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "Clicked '📍Biznig manzil")
    latitude = 41.189839
    longitude = 69.203384

    await update.message.reply_location(latitude=latitude, longitude=longitude)
    await update.message.reply_text("""📍 Bizning manzil:\n🏢 Energy Water Distribution Kompaniyasi\n
📌 Mo'ljal: Toshkent shahri, Yangihayot tumani, Do'stlik-2, Xushnud MFY\n
📌 Mo'ljal2: Avtobuslar 47.58.59.62.131.144 oxirgi bekati yoki Sport maktabi
📞 Aloqa: +998-99-580-33-33""")

async def reaching_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "📩Biz bilan bog'laning")
    file_id = "AgACAgIAAxkBAWqtb2fwDOAcJyafYa0CI2hC4liWuOKjAAJt7jEbj9qAS8p660JnJ0OKAQADAgADcwADNgQ"
    reply_keyboard = [
        ["🏠Bosh Menu","🔙 Orqaga"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    # Make the location clickable inside the caption using Markdown
    location_link = "[📍Bizning manzil](https://www.google.com/maps/@41.1898371,69.2031362,1047m/data=!3m1!1e3?authuser=0&entry=ttu&g_ep=EgoyMDI1MDMyNS4xIKXMDSoASAFQAw%3D%3D)"

    await update.message.reply_text(f"""Biz bilan bog'lanish uchun quyidagi raqamga qo'ng'iroq qiling👇\n

🔻Ma'lumotlar: \n
📩 telegram: @EnergyWD\n
☎️ +998-99-580-33-33\n
🕔 Ish vaqti: Dushanbadan Jumagacha 10:00 dan 17:00 gacha
✍️ Xabar qoldiring xodimlarimiz siz bilan aloqaga chiqishadi.
{location_link}""",parse_mode="Markdown", reply_markup=reply_markup)

    context.user_data["current_menu"] = "reaching_us"  # example

# Function to handle work button
async def job_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_activity(update, "💼Bo'sh ish o'rinlari")
    reply_keyboard = [
        ["Yukchi", "Haydovchi"],
        ["Expeditor", "Buxgalter"],
        ["Operator", "HR"],
        ["Karachi", "Ombor mudiri"],
        ["Hamshira", "Tozalik hodimi"],
        ["Logist", "Qorovul"],
        ["🏠Bosh Menu","🔙 Orqaga"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text("""✏️ Keling, anketani to'ldirishni boshlaylik\n

📕Instruksiya: Bot sizdan savollarni ketma-ket so'rab boradi,
siz barchasini to'liq kiritishingiz shart bu ishga olish bo'yicha mutaxasislarimiz tomonidan baholanadi, 
oxirida esa sizga tayyor rezyumi chiqarib beriladi.""", reply_markup=reply_markup)
    await update.message.reply_text("Kerakli bo'limni tanlang 👇", reply_markup=reply_markup)

    context.user_data["current_menu"] = "job_offer"  # example



async def start_questionnaire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_job = update.message.text
    if selected_job in job_questions:
        await update.message.reply_text(job_requirements[selected_job])
        context.user_data["job"] = selected_job
        context.user_data["answers"] = []
        context.user_data["question_index"] = 0
        context.user_data["follow_up_questions"] = []
        await ask_next_question(update, context)
    else:
        await update.message.reply_text("Iltimos, ro‘yxatdan ish turini tanlang.")

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job = context.user_data.get("job")
    index = context.user_data.get("question_index", 0)
    if job and index < len(job_questions[job]):
        question, options = job_questions[job][index]

        # Load the user's previous answers from the JSON file
        user_id = update.effective_user.id
        user_info = load_user_data(user_id)

        # Check if the current question has a previously answered value
        previous_answer = None
        if "Familiya" in question:
            previous_answer = user_info.get("full_name")
        elif "Tug'ilgan sana" in question:
            previous_answer = user_info.get("birthday")
        elif "manzil" in question:
            previous_answer = user_info.get("address")
        elif "tajriba" in question:
            previous_answer = user_info.get("tajriba")
        elif "qo‘shimcha" in question:
            previous_answer = user_info.get("qo‘shimcha")



        # You can add more mappings for other questions if needed


        # Define the keyboard
        if previous_answer:
            # If there's a previous answer, show it as a clickable option
            keyboard = [[previous_answer]]
            if options:
                for option in options:
                    keyboard.append([option])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        elif question == "Telefon raqamingiz?":
            keyboard = [[KeyboardButton("📞 Raqamni ulashish", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        elif options:
            reply_markup = ReplyKeyboardMarkup([[option] for option in options], resize_keyboard=True)
        else:
            reply_markup = ReplyKeyboardRemove()

        await update.message.reply_text(question, reply_markup=reply_markup)
        context.user_data["previous_index"] = index
    else:
        await send_resume(update, context)


def validate_birthday(text):
    formats = ["%d.%m.%Y", "%Y.%m.%d"]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None

def validate_full_name(name_text):
    # Allow letters, spaces, and hyphens (Uzbek names often have these)
    pattern = r"^[A-Za-zА-Яа-яЎўҚқҒғҲҳЁё\s\-']+$"
    return bool(re.match(pattern, name_text)) and 2 <= len(name_text) <= 50

async def store_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    answer = update.message.text
    job = context.user_data.get("job")
    index = context.user_data.get("question_index", 0)

    # Get the current question text
    current_question = job_questions[job][index][0]

    # Store the answer in context
    if "answers" not in context.user_data:
        context.user_data["answers"] = []

    # Add the answer to the list
    context.user_data["answers"].append(answer)

    # Now, let's store the answer in the user's information
    user_info = load_user_data(update.effective_user.id)

    print("Current answers:", context.user_data["answers"])
    # Map the question to a specific field
    if current_question == "Pasportdagi Familiya, Ism va Sharifini kiriting":
        user_info["full_name"] = answer
    elif current_question == "Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):":
        user_info["birthday"] = answer
    elif current_question == "Yashash manzilingiz (Viloyat, Tuman, ko'cha/kvartal, uy, kvartira):":
        user_info["address"] = answer
    elif current_question == """ "Oldingi ish tajribangiz? "
         "- tashkilot"
         "- lavozim"
         "- ishlagan vaqtingizni ko'rsating"
         "Misol: MCHJ 'Pepsi', Yukchi, 2020-2024" """:
        user_info["tajriba"] = answer
    elif current_question == "Sizni ishga olish uchun yana qanday qo‘shimcha ma’lumotlarni taqdim etishingiz mumkin?":
        user_info["qo‘shimcha"] = answer

    # Add more conditions as needed for other questions

    # Save the updated user info to JSON
    save_user_data(update.effective_user.id, user_info)

    # ✅ Validate full name
    if current_question == "Pasportdagi Familiya, Ism va Sharifini kiriting":
        if not validate_full_name(answer):
            await update.message.reply_text(
                "Iltimos, Familiya, Ism va Otasining ismini to‘liq va to‘g‘ri yozing. Masalan:\n\n"
                "`To‘xtayev Jasur Ismoil o‘g‘li`", parse_mode="Markdown"
            )
            return
        # context.user_data["answers"].append(answer)

    # ✅ Handle birthday input
    elif current_question == "Tug'ilgan sananingizni ko'rsating (misol, 12.10.2002):":
        birthday = validate_birthday(answer)
        if not birthday:
            await update.message.reply_text(
                "Iltimos, tug‘ilgan kuningizni to‘g‘ri formatda yozing. (Masalan: 25.12.2000 yoki 2000.12.25)"
            )
            context.user_data["answers"].pop()  # Remove invalid answer
            return  # Stop and wait for correct input
        # context.user_data["answers"].pop()  # Remove invalid answer
        formatted = birthday.strftime("%d-%m-%Y")
        # context.user_data["answers"][-1] = formatted
        # Check if the current question is the special one

    elif current_question == "Siz oldin sudlanganmisiz?" and answer == "Ha":
        # Don't increment the question index yet — ask follow-up
        context.user_data["awaiting_modda"] = True  # flag to track follow-up
        await update.message.reply_text("Qaysi modda bilan sudlangansiz? Shuni kiriting.", reply_markup=ReplyKeyboardRemove())
        context.user_data["answers"].pop()  # Remove invalid answer

        return

    elif current_question == "Siz talabamisiz?" and answer == "Ha":
        # Don't increment the question index yet — ask follow-up
        context.user_data["awaiting_student"] = True  # flag to track follow-up
        context.user_data["answers"].pop()  # Remove invalid answer

        await update.message.reply_text("Nechanchi kursda  va qaysi ta'lim shaklida ta'lim olasiz? (Kunduzgi, Kechgi, Sirtqi)",
                                        reply_markup=ReplyKeyboardRemove())
        return


    elif current_question == "Malumotlarimni qayta ishlashga roziman" and answer == "Yo'q":
        # Don't increment the question index yet — ask follow-up
        context.user_data["awaiting_malumot"] = True  # flag to track follow-up
        reply_keyboard = [
            ["🏠Bosh Menu", "🔙 Orqaga"]
        ]
        await update.message.reply_text("""Keyinroq urinib ko'ring""",
        reply_markup=ReplyKeyboardRemove())
        return

    # Save updated user info
    user_id = update.effective_user.id
    save_user_data(user_id, user_info)
    # Normal flow: go to the next question
    context.user_data["question_index"] += 1
    await ask_next_question(update, context)


async def store_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        context.user_data["answers"].append(contact.phone_number)  # Store the shared phone number
        context.user_data["question_index"] += 1
        await ask_next_question(update, context)

async def send_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job = context.user_data.get("job")
    answers = context.user_data.get("answers", [])
    if job and answers:
        resume_text = f"📄 Sizning anketangiz:\n\n💼 Lavozim: {job}\n"
        for (question, _), answer in zip(job_questions[job], answers):
            resume_text += f"{question}: {answer}\n"
        await update.message.reply_text("Siz ko'rib chiqish uchun nomzodlar ro'yxatiga kiritildingiz. Xodimlarimiz tez orada siz bilan bog'lanishadi.")
        await update.message.reply_text(resume_text, reply_markup=ReplyKeyboardRemove())

    # SEND TO HR
    questions = job_questions[job]

    summary = f"📨 Yangi ariza!\n💼 Lavozim: {job}\n\n"
    user_id = update.effective_user.id
    context.user_data["telegram_id"] = user_id

    for i, answer in enumerate(answers):
        question_text = questions[i][0] if i < len(questions) else "Qo‘shimcha ma'lumot"
        summary += f"*{question_text}*\n`{answer}`\n\n"

    try:
        await context.bot.send_message(
            chat_id=HR_ID and MY_ID,
            text=f"{summary}\n User_id: {user_id}",
        )
    except Exception as e:
        print("Error sending application to HR:", e)

    context.user_data.clear()



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    log_activity(update, f"Sent message: {text}")


    if text == "🍸Biz haqimizda":
        await about_us(update, context)
        return
    elif text == "🌍Bizning qadriyatlarimiz!":
        await our_traditions(update, context)
        return
    elif text == "🔙 Orqaga":
        await go_back(update, context)
        return
    elif text == "📍Biznig manzil":
        await send_actual_location(update, context)
        return
    elif text == "📩Biz bilan bog'laning":
        await reaching_us(update, context)
        return
    elif text == "💼Bo'sh ish o'rinlari":
        await job_offer(update, context)
        return
    elif text == "🏠Bosh Menu":
        await back_to_main(update, context)
        return

    # This goes in your main handler where you route messages
    elif context.user_data.get("awaiting_modda"):
        context.user_data["awaiting_modda"] = False  # clear flag
        context.user_data["answers"].append(f"Sudlangan: Ha, Modda: {text}")
        context.user_data["question_index"] += 1
        await ask_next_question(update, context)
        return

    # This goes in your main handler where you route messages
    elif context.user_data.get("awaiting_student"):
        context.user_data["awaiting_student"] = False  # clear flag
        context.user_data["answers"].append(f"Talaba: Ha, Ta'lim shakli: {text}")
        context.user_data["question_index"] += 1
        await ask_next_question(update, context)
        return

    # This goes in your main handler where you route messages
    elif context.user_data.get("awaiting_malumot"):
        context.user_data["awaiting_malumot"] = False  # clear flag
        context.user_data["answers"].append("Rozilik berilmadi")
        await back_to_main(update, context)
        return

    elif text in job_questions:
        await start_questionnaire(update, context)
        return
    elif context.user_data.get("job") and not any([
        context.user_data.get("awaiting_modda"),
        context.user_data.get("awaiting_malumot"),
        context.user_data.get("awaiting_student")
    ]):
        await store_answer(update, context)
    else:
        await update.message.reply_text("Kechirasiz, bu buyruqni tushunmadim.")
# Function to handle text messages

# Main function to run the bot
async def main():
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.CONTACT, store_contact))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    # asyncio.run(main())

    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())