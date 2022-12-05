import streamlit as st
import re
from PIL import Image, ImageChops, ImageEnhance

class Text:
    def __init__(self, text_area) -> None:
        self.text_area = text_area

    def to_file_name_list(self) -> list:
        replace_dict = {":": "CORON", ".": "PERIOD", "/": "SLASH", " ": "SPACE"}
        text_list = [replace_dict.get(char, char) for char in self.text_area.upper()]

        count, need_replace = 0, False  #「'」間の文字を置換
        for i, item in enumerate(text_list):
            if item=="'" and count<text_list.count("'")//2:
                if not need_replace:
                    need_replace = True
                else:
                    need_replace = False
                    count += 1
            if need_replace and item in [*map(str, range(10)), "-", "SLASH", "SPACE"]:
                text_list[i] += "_"

        #「'」を削除
        text_list = [item for item in text_list if item!="'"]
        # 右側の空白や改行を削除
        while len(text_list) and text_list[-1] in ["SPACE", "SPACE_", "\n"]:
            del text_list[-1]
        # 使用できない文字がないか検証
        text_list = [re.sub("[^-+0-9A-Z_,\n]", "", item) for item in text_list]
        # 検証時に生じた空文字とファイル名以外のアンダースコアを削除し、それを返す
        return [item for item in text_list if item not in ["", "_"]]

class UserInterface:
    def __init__(self, slider, selectbox) -> None:
        self.slider = slider
        self.selectbox = selectbox
        self.radio = "Vertical"

    def create_widget_if_needed(self, file_name_list):

        def set_top_color():
            st.session_state.top_color = st.session_state.color_picker_top

        def set_btm_color():
            st.session_state.btm_color = st.session_state.color_picker_btm

        if self.selectbox=="Color":
            st.session_state.color_picker_top = st.session_state.top_color
            st.sidebar.color_picker(
                "Pick a color",
                key="color_picker_top",
                on_change=set_top_color
                )
        if self.selectbox=="Colorful" and len(file_name_list):
            col1, col2 = st.sidebar.columns((1, 2))
            with col2:
                index = st.selectbox(  # インデックスの取得
                    "Select the character",
                    range(len(file_name_list)),
                    format_func=lambda x: file_name_list[x]
                    )

            def set_color_list():
                st.session_state.color_list[index] = st.session_state.color_picker_colorful

            with col1:
                st.session_state.color_picker_colorful = st.session_state.color_list[index]
                st.color_picker(
                    "Pick a color",
                    key="color_picker_colorful",
                    on_change=set_color_list
                    )
        if self.selectbox=="Gradient":
            self.radio = st.sidebar.radio(
                "radio",
                ("Vertical", "Horizontal"),
                horizontal=True,
                label_visibility="collapsed"
                )
            col3, col4 = st.sidebar.columns(2)
            with col3:
                st.session_state.color_picker_top = st.session_state.top_color
                st.color_picker(
                    "Top" if self.radio=="Vertical" else "Left",
                    key="color_picker_top",
                    on_change=set_top_color
                    )
            with col4:
                st.session_state.color_picker_btm = st.session_state.btm_color
                st.color_picker(
                    "Bottom" if self.radio=="Vertical" else "Right",
                    key="color_picker_btm",
                    on_change=set_btm_color
                    )

class TextGenerator:
    def __init__(self, file_name_list, selectbox, radio) -> None:
        self.file_name_list = file_name_list
        self.selectbox = selectbox
        self.radio = radio

    def create_image_list(self) -> list:
        image_list = []
        for file_name in self.file_name_list:
            if file_name=="\n":
                image_list.append("LF")  # LF: Line Feed (改行)
                continue

            if self.selectbox=="Yellow":
                image_list.append(Image.open(f"Fonts/Yellow/{file_name}.png"))
            else:
                image_list.append(Image.open(f"Fonts/White/{file_name}.png"))

        return image_list

    def gradient(self, size: tuple[int, int], top_color, btm_color) -> Image:
        base = Image.new("RGBA", size, top_color)
        top = Image.new("RGBA", size, btm_color)
        mask = Image.new("L", size)
        mask_data, width, height = [], *size  # アンパック
        for y in range(height):
            mask_data.extend([int(255*(y/height))]*width)
        mask.putdata(mask_data)
        base.paste(top, mask=mask)
        return base

    def multiply_char(self) -> list:
        image_list = self.create_image_list()
        #「Colorful」と「Gradient (Vertical)」以外は早期リターン
        if not (self.selectbox in ["Colorful", "Gradient"] and self.radio=="Vertical"):
            return image_list

        for i, image1 in enumerate(image_list):
            if image1=="LF":
                continue

            if self.selectbox=="Colorful":
                image2 = Image.new(
                    "RGBA",
                    image1.size,
                    st.session_state.color_list[i]
                    )
            if self.selectbox=="Gradient":
                image2 = self.gradient(
                    image1.size,
                    st.session_state.top_color,
                    st.session_state.btm_color
                    )
            image_list[i] = ImageChops.multiply(image1, image2)

        return image_list

    def update_x_coordinate(self, x, image_width, file_name):  # 文字に応じた結合位置の調整
        # 50: 0～9 & SLASH, 42: - & +
        if image_width in [50, 42] or file_name in ["PERIOD", "CORON"]:
            image_width -= 4
        else:
            image_width -= 12

        if file_name in ["T", "7_"]:
            image_width -= 6
        if file_name in ["I", "M", "CORON"]:
            image_width -= 2
        if file_name in ["L", "Q"]:
            image_width += 2

        x += image_width
        return x

    def concat_image(self) -> Image:
        image_list = self.multiply_char()
        y, is_LF = 0, False
        concated_image = Image.open("Fonts/Yellow/SPACE.png")  # エラー防止
        for i, image in enumerate(image_list):  # 画像の結合
            if image=="LF":  # 改行処理
                y += 64
                is_LF = True
                continue

            if i==0 or is_LF:
                x = 0
                image_width = image.width
                file_name = self.file_name_list[i]
                if i==0:  # 1文字目
                    concated_image = image
                if is_LF:  # 改行直後
                    bg = Image.new(
                        "RGBA",
                        (max(concated_image.width, image_width), y+64)
                        )
                    bg.paste(concated_image)
                    bg.paste(image, (0, y))
                    concated_image = bg
                    is_LF = False
            else:
                x = self.update_x_coordinate(x, image_width, file_name)
                image_width = image.width
                file_name = self.file_name_list[i]
                bg = Image.new(
                    "RGBA",
                    (max(concated_image.width, x+image_width), y+64)
                    )
                bg.paste(concated_image)
                fg = Image.new("RGBA", bg.size)
                fg.paste(image, (x, y))
                concated_image = Image.alpha_composite(bg, fg)

        return concated_image

    def multiply_str(self) -> Image:
        concated_image = self.concat_image()
        #「Color」と「Gradient (Horizontal)」以外は早期リターン
        if not (self.selectbox=="Color" or self.radio=="Horizontal"):
            return concated_image

        if self.selectbox=="Color":
            image2 = Image.new(
                "RGBA",
                concated_image.size,
                st.session_state.top_color
                )
        if self.radio=="Horizontal":
            image2 = self.gradient(
                (concated_image.height, concated_image.width),
                st.session_state.top_color,
                st.session_state.btm_color
                )
            image2 = image2.transpose(Image.Transpose.ROTATE_90)
        return ImageChops.multiply(concated_image, image2)

    def generate_image(self, slider) -> Image:
        color_image = self.multiply_str()
        enhancer = ImageEnhance.Brightness(color_image)  # 明るさ調整
        return enhancer.enhance(slider)


def main():
    st.set_page_config(
        page_title="MKWii Text Generator",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": "https://github.com/NOKKY726/mkwii-text-generator"
            }
        )

    if "top_color" not in st.session_state:
        st.session_state.top_color = "#f00"
        st.session_state.btm_color = "#0f0"
        st.session_state.color_list = ["#fff" for _ in range(10000)]

    text = Text(st.sidebar.text_area("text_area", label_visibility="collapsed"))
    file_name_list = text.to_file_name_list()

    user_interface = UserInterface(
        st.sidebar.slider("Brightness", step=5)/50+1,  # 1 to 3
        st.sidebar.selectbox(
            "selectbox",
            ("Yellow", "White", "Color", "Colorful", "Gradient"),
            label_visibility="collapsed"
            )
        )
    user_interface.create_widget_if_needed(file_name_list)
    link = "[Developer's Twitter](https://twitter.com/nkfrom_mkw/)"
    st.sidebar.markdown(link, unsafe_allow_html=True)
    checkbox = st.sidebar.checkbox("Mobile")

    text_generator = TextGenerator(
        file_name_list,
        user_interface.selectbox,
        user_interface.radio
        )
    MKWii_text = text_generator.generate_image(user_interface.slider)

    if not checkbox:
        st.image(MKWii_text)
    else:
        st.sidebar.image(MKWii_text)

if __name__ == "__main__":
    main()
