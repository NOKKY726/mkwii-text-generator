import streamlit as st
import re
from PIL import Image, ImageChops, ImageEnhance


st.set_page_config(page_title="MKWii Text Generator", layout="wide")

if "top_color" not in st.session_state:  # 初期化
    st.session_state.top_color = "#f00"
    st.session_state.btm_color = "#0f0"
    st.session_state.color_list = ["#fff" for _ in range(10000)]

text = st.sidebar.text_area("text_area", label_visibility="collapsed")
slider = st.sidebar.slider("Brightness", step=5)/50+1
selectbox = st.sidebar.selectbox(
    "selectbox",
    ("Yellow", "White", "Color", "Colorful", "Gradient"),
    label_visibility="collapsed"
    )


text = ",".join(list(text)).upper()  # 分割したものを「,」で連結
quot_pos = [m.start() for m in re.finditer("'", text)]  #「'」の位置を取得
# 置換するための辞書を用意
replace_dict1 = {
    "1":"1_", "2":"2_", "3":"3_", "4":"4_", "5":"5_",
    "6":"6_", "7":"7_", "8":"8_", "9":"9_", "0":"0_",
    "-":"-_", "/":"SLASH_", " ":"SPACE_"
    }
#「'」間の文字を「replace_dict1」に従って置換
if len(quot_pos)>=2:
    for i in range(len(quot_pos)//2):
        p1 = quot_pos[i*2]+1
        p2 = quot_pos[i*2+1]
        replace_font = text[p1:p2].translate(str.maketrans(replace_dict1))
        text = text[0:p1]+replace_font+text[p2:len(text)]
        quot_pos = [m.start() for m in re.finditer("'", text)]

#「'」を空文字に変換後、両端に「,」があれば削除
text = text.replace("'", "").strip(",")
# 右側の改行や空白を削除
while text[-2:]==",\n" or text[-2:]==", " or text[-7:]==",SPACE_":
    text = text.rstrip(",\n").rstrip(", ").removesuffix(",SPACE_")
# 使用できない文字を空文字に変換 (validation: 検証)
text = re.sub(re.compile("[^0-9A-Z-+:./_', \n]"), "", text)
#「,」で分割
text = text.split(",")
#「'」の変換時や検証時に生じた空文字とファイル名以外のアンダーバーを削除
text = [elm for elm in text if elm!="" and elm!="_"]
# ファイル名として使えない文字を「replace_dict2」に従って変換
replace_dict2 = {":":"CORON", ".":"PERIOD", "/":"SLASH", " ":"SPACE"}
file_name_list = [replace_dict2.get(elem, elem) for elem in text]


def set_top_color():
    st.session_state.top_color = st.session_state.color_picker_top
def set_btm_color():
    st.session_state.btm_color = st.session_state.color_picker_btm
def set_color_list():
    st.session_state.color_list[index] = \
        st.session_state.color_picker_colorful

if selectbox=="Color":
    st.session_state.color_picker_top = st.session_state.top_color
    st.sidebar.color_picker(
        "Pick A Color",
        key="color_picker_top",
        on_change=set_top_color
        )
elif selectbox=="Colorful" and len(file_name_list):
    col1, col2 = st.sidebar.columns((1, 2))
    with col2:
        options = file_name_list  # インデックス番号の取得
        index = st.selectbox(
            "Select The Character",
            range(len(options)),
            format_func=lambda x: options[x]
            )
    with col1:  #「color_picker」を「session_state」で管理
        st.session_state.color_picker_colorful = \
            st.session_state.color_list[index]
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


def gradient(top_color, btm_color, width, height):
    base = Image.new("RGBA", (width, height), top_color)
    top = Image.new("RGBA", (width, height), btm_color)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255*(y/height))]*width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

img_list = []  # 画像を読み込み、追加していく
for i, file_name in enumerate(file_name_list):
    if file_name=="\n":  # 改行時は「None」をリストに追加
        open_img = None

    elif selectbox=="Yellow":
        open_img = Image.open(f"Fonts/Yellow/{file_name}.png")
    else:
        open_img = Image.open(f"Fonts/White/{file_name}.png")
        # 1文字ずつ乗算する (「Color」は後からまとめて行う)
        if selectbox=="Colorful" or selectbox=="Gradient":
            if selectbox=="Colorful":
                effect_img = Image.new(
                    "RGBA",
                    (open_img.width, open_img.height),
                    st.session_state.color_list[i]
                    )
            else:
                effect_img = gradient(
                    st.session_state.top_color,
                    st.session_state.btm_color,
                    open_img.width,
                    open_img.height)
            open_img = ImageChops.multiply(open_img, effect_img)

    img_list.append(open_img)


def concat_pos(img_width, file_name, x):  # 文字に応じた幅の調整
    #50: 0～9 & SLASH, 42: - & +
    if img_width!=50 and img_width!=42 \
        and file_name!="PERIOD" and file_name!="CORON":
        img_width -= 12
    else:
        img_width -= 4

    if file_name=="T" or file_name=="7_":
        img_width -= 6
    if file_name=="I" or file_name=="M":
        img_width -= 2
    if file_name=="L" or file_name=="Q":
        img_width += 2

    x += img_width
    return x

y = 0
lf_flag = False
concat_img = Image.open("Fonts/Yellow/SPACE.png")  #  エラー防止
for i in range(len(img_list)):  # 画像の結合
    if img_list[i]!=None:
        if i==0 or lf_flag==True:
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
            bg.paste(img_list[i], (0, y))
            concat_img = bg
            lf_flag = False
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
    else:  # 改行時の処理
        y += 64
        lf_flag = True


if selectbox=="Color":
    effect_img = Image.new(
        "RGBA",
        (concat_img.width, concat_img.height),
        st.session_state.top_color
        )
    concat_img = ImageChops.multiply(concat_img, effect_img)


enhancer = ImageEnhance.Brightness(concat_img)
display_img = enhancer.enhance(slider)

st.image(display_img)


link = "[Developer's Twitter](https://twitter.com/nkfrom_mkw)"
st.sidebar.markdown(link, unsafe_allow_html=True)
