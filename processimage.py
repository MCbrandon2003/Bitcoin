from PIL import Image

def change_background_to_transparent(image_path, output_path):
    # 打开图像
    img = Image.open(image_path).convert("RGBA")

    # 获取原点的颜色
    background_color = img.getpixel((10, 10))

    # 创建一个新图像，大小与原图相同，带有透明背景
    new_img = Image.new("RGBA", img.size, (0, 0, 0, 0))

    # 获取图像数据
    pixels = img.load()
    new_pixels = new_img.load()

    # 遍历每个像素
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            current_color = pixels[x, y]
            if current_color[:3] == background_color[:3]:  # 忽略透明度通道，比较RGB值
                new_pixels[x, y] = (0, 0, 0, 0)  # 透明
            else:
                new_pixels[x, y] = current_color  # 保留原始像素

    # 保存新图像
    new_img.save(output_path, "PNG")

if __name__ == "__main__":
    change_background_to_transparent("summary extraction.png", "images/summary extraction.png")