# -*- coding: utf-8 -*-
import random


def id_generator(size=8, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
	return "".join(random.choice(chars) for x in range(size))

if __name__ == "__main__":
	print id_generator()
