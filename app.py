import streamlit as st
import re
from PIL import Image, ImageChops, ImageEnhance

st.set_page_config(page_title="MKWii Text Generator", layout="wide")

if "top_color" not in st.session_state:  # 初期化
    st.session_state.top_color = "#f00"
    st.session_state.btm_color = "#0f0"
    st.session_state.color_list = ["#fff" for _ in range(10000)]

text = st.sidebar.text_area("text_area", label_visibility="collapsed").upper()
slider = st.sidebar.slider("Brightness", step=5)/50+1
selectbox = st.sidebar.selectbox(
    "selectbox",
    ("Yellow", "White", "Color", "Colorful", "Gradient"),
    label_visibility="collapsed"
    )


# ファイル名として使えない文字を「replace_dict」に従って置換
replace_dict = {":":"CORON", ".":"PERIOD", "/":"SLASH", " ":"SPACE"}
text = [replace_dict.get(elem, elem) for elem in text]

cnt, need_replace = 0, False  #「'」間の文字を置換
for i, elem in enumerate(text):
    if elem=="'" and cnt<text.count("'")//2:
        if not need_replace:
            need_replace = True
        else:
            need_replace = False
            cnt += 1
    elif need_replace and (text[i].isdecimal() or text[i] in ["-", "SLASH", "SPACE"]):
        text[i] += "_"

#「'」を削除し、「,」で連結
text = ",".join([elem for elem in text if elem!="'"])
# 右側の改行や空白を削除
while text[-2:]==",\n" or text[-2:]==", " or text[-7:]==",SPACE_":
    text = text.rstrip(",\n").rstrip(", ").removesuffix(",SPACE_")
# 使用できない文字を空文字に置換 (validation: 検証)
text = re.sub("[^-+0-9A-Z_,\n]", "", text)
# 検証時に生じた空文字とファイル名以外のアンダースコアを削除
file_name_list = [elem for elem in text.split(",") if elem!="" and elem!="_"]


def set_top_color():
    st.session_state.top_color = st.session_state.color_picker_top
def set_btm_color():
    st.session_state.btm_color = st.session_state.color_picker_btm
def set_color_list():
    st.session_state.color_list[index] = st.session_state.color_picker_colorful

if selectbox=="Color":  #「color_picker」を「session_state」で管理
    st.session_state.color_picker_top = st.session_state.top_color
    st.sidebar.color_picker(
        "Pick A Color",
        key="color_picker_top",
        on_change=set_top_color
        )
elif selectbox=="Colorful" and len(file_name_list):
    col1, col2 = st.sidebar.columns((1, 2))
    with col2:
        options = file_name_list  # インデックスの取得
        index = st.selectbox(
            "Select The Character",
            range(len(options)),
            format_func=lambda x: options[x]
            )
    with col1:
        st.session_state.color_picker_colorful = st.session_state.color_list[index]
        st.color_picker(
            "Pick A Color",
            key="color_picker_colorful",
            on_change=set_color_list
            )
elif selectbox=="Gradient":
    col3, col4 = st.sidebar.columns(2)
    with col3:
        st.session_state.color_picker_top = st.session_state.top_color
        st.color_picker(
            "Pick A Top Color",
            key="color_picker_top",
            on_change=set_top_color
            )
    with col4:
        st.session_state.color_picker_btm = st.session_state.btm_color
        st.color_picker(
            "Pick A Bottom Color",
            key="color_picker_btm",
            on_change=set_btm_color
            )


def gradient(top_color, btm_color, size: tuple[int, int]):
    base = Image.new("RGBA", size, top_color)
    top = Image.new("RGBA", size, btm_color)
    mask = Image.new("L", size)
    mask_data, width, height = [], *size  # アンパック
    for y in range(height):
        mask_data.extend([int(255*(y/height))]*width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

img_list = []  # 画像を読み込み、追加していく
for i, file_name in enumerate(file_name_list):
    if file_name=="\n":  # 改行は「None」で判定
        open_img = None

    elif selectbox=="Yellow":
        open_img = Image.open(f"Fonts/Yellow/{file_name}.png")
    else:
        open_img = Image.open(f"Fonts/White/{file_name}.png")
        # 1文字ずつ乗算 (「Color」は後からまとめて行う)
        if selectbox=="Colorful" or selectbox=="Gradient":
            if selectbox=="Colorful":
                effect_img = Image.new(
                    "RGBA",
                    open_img.size,
                    st.session_state.color_list[i]
                    )
            else:
                effect_img = gradient(
                    st.session_state.top_color,
                    st.session_state.btm_color,
                    open_img.size)
            open_img = ImageChops.multiply(open_img, effect_img)

    img_list.append(open_img)


def concat_pos(img_width, file_name, x):  # 文字に応じた幅の調整
    # 50: 0～9 & SLASH, 42: - & +
    if img_width in [50, 42] or file_name in ["PERIOD", "CORON"]:
        img_width -= 4
    else:
        img_width -= 12

    if file_name in ["T", "7_"]:
        img_width -= 6
    if file_name in ["I", "M", "CORON"]:
        img_width -= 2
    if file_name in ["L", "Q"]:
        img_width += 2

    x += img_width
    return x

y, is_LF = 0, False  # LF: Line Feed (改行)
concat_img = Image.open("Fonts/Yellow/SPACE.png")  # エラー防止
for i in range(len(img_list)):  # 画像の結合
    if img_list[i]!=None:
        if i==0 or is_LF==True:
            x = 0
            img_width = img_list[i].width
            file_name = file_name_list[i]
            if i==0:  # 1文字目
                bg = Image.new("RGBA", (img_width, y+64))
            else:  # 改行直後
                bg = Image.new(
                    "RGBA",
                    (max(concat_img.width, img_width), y+64)
                    )
                bg.paste(concat_img, (0, 0))
                is_LF = False
            bg.paste(img_list[i], (0, y))
            concat_img = bg
        else:
            x = concat_pos(img_width, file_name, x)
            img_width = img_list[i].width
            file_name = file_name_list[i]
            bg = Image.new(
                "RGBA",
                (max(concat_img.width, x+img_width), y+64)
                )
            bg.paste(concat_img, (0, 0))
            img_clear = Image.new("RGBA", bg.size)
            img_clear.paste(img_list[i], (x, y))
            concat_img = Image.alpha_composite(bg, img_clear)
    else:  # 改行処理
        y += 64
        is_LF = True


if selectbox=="Color":
    effect_img = Image.new(
        "RGBA",
        concat_img.size,
        st.session_state.top_color
        )
    concat_img = ImageChops.multiply(concat_img, effect_img)


enhancer = ImageEnhance.Brightness(concat_img)  # 明るさ調整
display_img = enhancer.enhance(slider)

st.image(display_img)


link = "[Developer's Twitter](https://twitter.com/nkfrom_mkw)"
st.sidebar.markdown(link, unsafe_allow_html=True)
