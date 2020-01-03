# -*- coding: utf-8 -*-
"""
 @File    : generator.py
 @Time    : 2019/12/22 下午8:22
 @Author  : yizuotian
 @Description    :  中文数据生成器
"""
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from torch.utils.data.dataset import Dataset


def random_color(lower_val, upper_val):
    return [random.randint(lower_val, upper_val),
            random.randint(lower_val, upper_val),
            random.randint(lower_val, upper_val)]


def put_text(image, x, y, text, font, color=None):
    """
    写中文字
    :param image:
    :param x:
    :param y:
    :param text:
    :param font:
    :param color:
    :return:
    """

    im = Image.fromarray(image)
    draw = ImageDraw.Draw(im)
    color = (255, 0, 0) if color is None else color
    draw.text((x, y), text, color, font=font)
    return np.array(im)


class Generator(Dataset):
    def __init__(self, alpha):
        super(Generator, self).__init__()
        # self.alpha = ' 0123456789abcdefghijklmnopqrstuvwxyz'
        self.alpha = alpha
        self.min_len = 5
        self.max_len_list = [16, 19, 24, 26]
        self.max_len = max(self.max_len_list)
        self.font_size_list = [30, 25, 20, 18]
        self.font_list = [ImageFont.truetype('fonts/simsun.ttc', size=s) for s in self.font_size_list]

    @classmethod
    def gen_background(cls):
        a = random.random()
        if a < 0.1:
            return np.random.rand(32, 512, 3) * 100
        elif a < 0.8:
            return np.zeros((32, 512, 3)) * np.array(random_color(0, 100)) * 100 / 255
        else:
            b = random.random()
            return b * np.random.rand(32, 512, 3) * 100 + \
                   (1 - b) * np.zeros((32, 512, 3)) * np.array(random_color(0, 100)) * 100 / 255

    def gen_image(self):
        idx = np.random.randint(len(self.max_len_list))
        image = self.gen_background()
        image = image.astype(np.uint8)
        target_len = int(np.random.uniform(self.min_len, self.max_len_list[idx], size=1))
        indices = np.random.choice(range(1, len(self.alpha)), target_len)
        text = [self.alpha[idx] for idx in indices]
        color = random_color(105, 255)
        image = put_text(image, 3, np.random.randint(1, 32 - self.font_size_list[idx]), ''.join(text),
                         self.font_list[idx], tuple(color))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if random.random() > 0.5:
            image = 255 - image
        return image, indices, target_len

    def __getitem__(self, item):
        image, indices, target_len = self.gen_image()
        image = np.transpose(image[:, :, np.newaxis], axes=(2, 1, 0))  # [H,W,C]=>[C,W,H]
        image = image.astype(np.float32) / 255.
        image -= 0.5
        image /= 0.5
        target = np.zeros(shape=(self.max_len,), dtype=np.long)
        target[:target_len] = indices
        input_len = 31
        return image, target, input_len, target_len

    def __len__(self):
        return len(self.alpha) * 100


def test_image_gen():
    from config import cfg
    gen = Generator(cfg.word.get_all_words())
    for i in range(10):
        im, indices, target_len = gen.gen_image()
        cv2.imwrite('images/examples-{:02d}.jpg'.format(i + 1), im)
        print(''.join([gen.alpha[j] for j in indices]))


def test_gen():
    from data.words import Word
    gen = Generator(Word().get_all_words())
    for x in gen:
        print(x[1])


def test_font_size():
    font = ImageFont.truetype('fonts/simsun.ttc')
    print(font.size)
    font.size = 20
    print(font.size)


if __name__ == '__main__':
    test_image_gen()
    # test_gen()
    # test_font_size()
