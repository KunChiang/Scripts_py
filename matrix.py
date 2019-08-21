import os
import time
import numpy as np
# 获取控制台的尺寸，实际宽度为column/3(mac)
rows, columns = os.popen('stty size', 'r').read().split()
print("row: {}, columns: {}".format(rows, columns))
zfs = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(45, 58)] + ['.'] + [' ']*50
while True:
	mats = []
	for i in range(int(int(columns)/3)):
		mats.append(np.random.choice(zfs))
		#mats.append(np.random.choice([0,1]))
	# \ 033 [显示方式;字体色;背景色m ...... [\ 033 [0m]
	# 显示方式	效果	字体色	背景色	颜色描述
	# 0		终端默认设置	30	40		黑色
	# 1		高亮显示		31	41		红色
	# 4		使用下划线		32	42		绿色
	# 5		闪烁			33	43		黄色
	# 7		反白显示		34	44		蓝色
	# 8		不可见			35	45		紫红色
	# 						36	46		青蓝色
	# 						37	47		白色
	print("\033[1;32m {} \033[0m".format('  '.join(mats)))
	#break
	time.sleep(0.08)
