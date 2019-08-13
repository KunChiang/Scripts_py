# coding:utf-8
import argparse
import multiprocessing as mp
import os
from itertools import permutations

import rarfile
from tqdm import tqdm

FLAGS = None
pwd_dict_file = "./data/pwd_dict.txt"

def unrar(filepath, pwd, savepath="./"):
    file = rarfile.RarFile(filepath)
    if savepath == 'rawpath':
        savepath = "/".join(savepath.split("/")[:-1])
        # print(savepath)
    elif savepath == 'thispath':
        savepath = "./"
    file.extractall(path=savepath, pwd=pwd)
    file.close()

def mp_job(pwd):
    try:
        unrar(file, pwd, targetpath)
        return True
    except:
        return False

parser = argparse.ArgumentParser()
parser.add_argument('--filepath', type=str, default='', help='Help information')
parser.add_argument('--targetpath', type=str, default='./', help='Help information')
parser.add_argument('--searchtimes', type=int, default=int(10e4), help='Help information')
FLAGS, unparsed = parser.parse_known_args()

file = FLAGS.filepath
targetpath = FLAGS.targetpath
searchtimes = FLAGS.searchtimes
file = ""
pwd_dict = set()
if os.path.exists(pwd_dict_file):
    with open(pwd_dict_file, 'r') as f:
        for l in f:
            pwd_dict.add(l.strip())
unrar_flag = False
for pwd in pwd_dict:
    try:
        unrar(file, pwd, targetpath)
        unrar_flag = True
    except:
        pass
if not unrar_flag:
    zm = [chr(i) for i in range(33, 127)] # 33~127
    lgths = range(4, 16)
    for i in lgths:
        print("Trying password length:", i)
        pwds = [''.join(list(c)) for c in  permutations(zm, i)]
        print("Search Space:", len(pwds))
        pool = mp.Pool()
        reslist = pool.map(mp_job, pwds[:searchtimes])
    pwd = pwds[reslist.index(True)] if True in reslist else ''

if unrar_flag:
    pwd_dic_f = open(pwd_dict_file, 'a')
    pwd_dic_f.write(pwd+'\n')
    pwd_dic_f.close()

print("Unrar success if: ", unrar_flag, 'pwd: ', pwd)

