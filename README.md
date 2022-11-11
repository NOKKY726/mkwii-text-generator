# MKWii Text Generator
![demo](https://user-images.githubusercontent.com/117383835/201029512-db1c7105-6275-4315-abda-a91c3772db06.gif)
## URL
https://nokky-mkwii-text-generator.streamlit.app/
## Overview
マリオカートWiiのフォントを使用し、様々な文字列の画像を作成できます。  
色の変更も可能です。サムネイル等にお使いください。
## Description
使用することができる文字は　A～Z　0～9　:　.　+　-　/　です。  
0～9 と - / には 2つ目のフォントが用意されており、シングルクォーテーションで囲むことにより使用できます。  
また、シングルクォーテーションで囲んだ空白は通常のものと比べて 6分の1 の長さになっています。  
ラップタイムを再現すると、下のようになります。
<pre>
LAP '1   '  00:23.018
LAP '2'  00:22.884
LAP '3'  00:22.872
</pre>
右クリックから画像を保存することができます。
## Requirement
- Windows 10
- Python 3.9.12
- Streamlit 1.13.0
- Pillow 9.2.0
## Usage
```streamlit run app.py```
## Author
[Twitter](https://twitter.com/nkfrom_mkw)
## License
[MIT](https://github.com/NOKKY726/mkwii-text-generator/blob/main/LICENSE)
