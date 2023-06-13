from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

PGUSER = env.str("PGUSER")
PGPASSWORD = env.str("PGPASSWORD")
DATABASE = env.str("DATABASE")

POSTGRES_URI = f"postgresql://{PGUSER}:{PGPASSWORD}@{IP}/{DATABASE}"

BOT_NAME = env.str("BOTNAME")

SEC_TO_DEL = env.int("SECTODEL") # количество секунд на считывание QR-кода (удаляется)

PAYMENT_PERCENT = env.float("PAYMENTPERCENT") # процент списания баллов максимальный
EARN_PERCENT = env.float("EARNPERCENT") # процент начисления баллов от суммы покупки

URL_TO_SAVE_PHOTO = env.str("URLTOSAVEPHOTO") # куда сохраняются фотографии для сайта (каталог)
URL_TO_SAVE_PHOTO_PROMO = env.str("URLTOSAVEPHOTOPROMO") # куда сохраняются фотографии для сайта (акции)

ADD_REFFERAL = env.int("ADDREFFERAL") # СКОЛЬКО НАЧИСЛИТСЯ ТОМУ, КОГО ПРИГЛАСИЛИ
ADD_REFFER = env.int("ADDREFFER") # СКОЛЬКО НАЧИСЛИТСЯ ТОМУ, КТО ПРИГЛАСИЛ

URL_SITE = env.str("URLSITE") # ссылка на сайт с каталогом
