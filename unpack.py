# coding:utf-8
import rarfile
import argparse
import os
from itertools import permutations
from tqdm import tqdm

FLAGS = None
pwd_dict_file = "./pwd_dict.txt"

def unrar(filepath, pwd, savepath="./"):
    file = rarfile.RarFile(filepath)
    if savepath == 'rawpath':
        savepath = "/".join(savepath.split("/")[:-1])
        print(savepath)
    elif savepath == 'thispath':
        savepath = "./"
    file.extractall(path=savepath, pwd=pwd)
    file.close()

def search_pwd(file, targetpath, maxsearch=100000):
    count = 0
    zm = [chr(i) for i in range(33, 127)]
    lgths = range(4, 16)
    for i in tqdm(lgths):
        pwds = [''.join(list(c)) for c in  permutations(zm, i)]
        for pwd in tqdm(pwds):
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
        unrar_flag, pwd = search_pwd(file, targetpath)

    if unrar_flag:
        pwd_dic_f = open(pwd_dict_file, 'a')
        pwd_dic_f.write(pwd+'\n')
        pwd_dic_f.close()

    print("Unrar success if: ", unrar_flag, 'pwd: ', pwd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default='', help='Help information')
    parser.add_argument('--targetpath', type=str, default='./', help='Help information')
    FLAGS, unparsed = parser.parse_known_args()
    main()