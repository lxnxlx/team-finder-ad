import json
import re
from io import BytesIO
from urllib.parse import urlparse
import uuid

from django import forms
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont


PAGE_SIZE = 12
PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")
PHONE_WITH_EIGHT_LENGTH = 11

AVATAR_GREEN_COLOR = "#3A7D7C"
AVATAR_PURPLE_COLOR = "#7A5C99"
AVATAR_BROWN_COLOR = "#9C6B30"
AVATAR_BLUE_COLOR = "#3F6EA8"
AVATAR_OLIVE_COLOR = "#5F7A3D"
AVATAR_RED_COLOR = "#8B4A54"
AVATAR_TEXT_COLOR = "white"
AVATAR_BACKGROUND_MODE = "RGB"
AVATAR_IMAGE_FORMAT = "PNG"
AVATAR_FONT_NAME = "Arial.ttf"
AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 128
AVATAR_Y_SHIFT = 8
FIRST_LETTER_INDEX = 0
BBOX_LEFT_INDEX = 0
BBOX_TOP_INDEX = 1
BBOX_RIGHT_INDEX = 2
BBOX_BOTTOM_INDEX = 3
HALF_DIVIDER = 2
ZERO_COORDINATE = 0


def paginate_items(request, items, page_size=PAGE_SIZE):
    paginator = Paginator(items, page_size)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def get_request_data(request):
    if request.content_type == "application/json":
        try:
            if request.body:
                return json.loads(request.body)
            return {}
        except json.JSONDecodeError:
            return {}
    return request.POST


def normalize_phone(value):
    if value is None:
        return ""

    phone = value.strip()
    if phone.startswith("8") and len(phone) == PHONE_WITH_EIGHT_LENGTH:
        phone = "+7" + phone[1:]
    return phone


def validate_phone_format(phone):
    if phone and not PHONE_RE.match(phone):
        raise forms.ValidationError("Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")


def validate_github_url(value):
    if not value:
        return

    parsed_url = urlparse(value)
    host = parsed_url.netloc.lower()
    if host not in {"github.com", "www.github.com"}:
        raise forms.ValidationError("Ссылка должна вести на github.com")


def get_avatar_filename():
    return f"avatar_{uuid.uuid4()}.png"


def build_initial_avatar(file_name, name, email):
    colors = [
        AVATAR_GREEN_COLOR,
        AVATAR_PURPLE_COLOR,
        AVATAR_BROWN_COLOR,
        AVATAR_BLUE_COLOR,
        AVATAR_OLIVE_COLOR,
        AVATAR_RED_COLOR,
    ]

    text_for_color = email
    if not text_for_color:
        text_for_color = name

    total = 0
    for symbol in text_for_color:
        total += ord(symbol)
    color_number = total % len(colors)
    color = colors[color_number]

    image = Image.new(AVATAR_BACKGROUND_MODE, (AVATAR_SIZE, AVATAR_SIZE), color)
    draw = ImageDraw.Draw(image)

    if name:
        letter = name[FIRST_LETTER_INDEX]
    elif email:
        letter = email[FIRST_LETTER_INDEX]
    else:
        letter = "?"
    letter = letter.upper()

    try:
        font = ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((ZERO_COORDINATE, ZERO_COORDINATE), letter, font=font)
    text_width = bbox[BBOX_RIGHT_INDEX] - bbox[BBOX_LEFT_INDEX]
    text_height = bbox[BBOX_BOTTOM_INDEX] - bbox[BBOX_TOP_INDEX]
    x = (AVATAR_SIZE - text_width) / HALF_DIVIDER
    y = (AVATAR_SIZE - text_height) / HALF_DIVIDER - AVATAR_Y_SHIFT
    draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

    output = BytesIO()
    image.save(output, format=AVATAR_IMAGE_FORMAT)
    return ContentFile(output.getvalue(), name=file_name)
