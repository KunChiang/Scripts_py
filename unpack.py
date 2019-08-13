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

def search_pwd(file, targetpath, maxsearch):
    count = 0
    zm = [chr(i) for i in range(33, 127)]
    lgths = range(4, 16)
    for i in tqdm(lgths, desc='pwd length'):
        pwds = [''.join(list(c)) for c in  permutations(zm, i)]
        for pwd in tqdm(pwds, desc='search space'):
            count += 1
            if count >= maxsearch:
                return False, ''
            try:
                unrar(file, pwd, targetpath)
                return True, pwd
            except:
                pass

def main():
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
        unrar_flag, pwd = search_pwd(file, targetpath, searchtimes)

    if unrar_flag:
        pwd_dic_f = open(pwd_dict_file, 'a')
        pwd_dic_f.write(pwd+'\n')
        pwd_dic_f.close()
        print("Unpack success! pwd: ", pwd, "savePath: ", targetpath)
    else:
        print("Unpack Failed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default='', help='Help information')
    parser.add_argument('--targetpath', type=str, default='./', help='Help information')
    parser.add_argument('--searchtimes', type=int, default=int(10e4), help='Help information')
    FLAGS, unparsed = parser.parse_known_args()
    main()
