# Константы для модели User
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256
PASSWORD_MIN_LENGTH = 8

# Константы для валидации телефона
PHONE_DIGITS_LENGTH_1 = 10
PHONE_DIGITS_LENGTH_2 = 11
PHONE_START_DIGIT = '8'
PHONE_REPLACE_DIGIT = '7'

# Фильтры
FILTER_AUTHORS_OF_FAVORITE = 'owners-of-favorite-projects'
FILTER_AUTHORS_OF_PARTICIPATING = 'owners-of-participating-projects'
FILTER_INTERESTED_IN_MY = 'interested-in-my-projects'
FILTER_PARTICIPANTS_OF_MY = 'participants-of-my-projects'

FILTER_BUTTONS = {
    FILTER_AUTHORS_OF_FAVORITE: 'Авторы избранных проектов',
    FILTER_AUTHORS_OF_PARTICIPATING: 'Авторы проектов, в которых я участвую',
    FILTER_INTERESTED_IN_MY: 'Пользователи, которым нравятся мои проекты',
    FILTER_PARTICIPANTS_OF_MY: 'Участники моих проектов',
}

# Палитра цветов для аватаров
AVATAR_COLORS = [
    '#FF0000',
    '#00FF00',
    '#0000FF',
    '#FFA500',
    '#800080',
    '#00008B',
    '#FFC0CB',
]

# Параметры аватара
AVATAR_SIZE = 200
AVATAR_TEXT_SIZE = 120
AVATAR_FONT_PATH = (
    "static/fonts/"
    "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
)

USERS_PER_PAGE = 12
