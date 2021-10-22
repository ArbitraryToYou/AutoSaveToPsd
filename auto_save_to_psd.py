#################################################
#Datatime:2021/10/17
#Author:Joky
#Description:Auto save all layers to a psd file.
#################################################

from time import sleep
from os import system
from os import rename
from os import remove
from os import makedirs
from os import path as opath
from photoshop import Session
from config import global_config

def get_path() -> str:
    while True:
        print('请选择保存目录[1~3]：')
        print('1.桌面\n2.D盘根目录\n3.自定义')
        while True:
            try:
                choice = int(input('->'))
                break
            except:
                print('[参数不合法！重新选择。]\n')
        if choice == 1:
            return opath.join(opath.expanduser('~'), 'Desktop\\自动备份\\')
        elif choice == 2:
            try:
                if opath.exists('D:\\'):
                    return 'D:\\自动备份\\'   
            except:
                print('[找不到相应的路径。]\n')
        elif choice == 3:
            path = input('目标路径：')
            index = path.find(':\\')
            if -1 == index:
                print('[自定义路径不合法！格式：D:\\xxx\\]\n')
            else:
                if path[-1] != '\\':
                    return path + '\\'
                else: return path
        else:
            print("[选项不合法。]\n")

def check_path(path : str) -> bool:
    return opath.exists(path) and opath.isfile(path)

def make_path(path : str):
    if not opath.exists(path):
        makedirs(path)

def get_stop_time() -> int:
    try:
        alternate = int(input('保存间隔(default 300s)：'))
        return alternate if alternate >= 10 else 60*5
    except:
        return 60*5

def get_max_fail_num() -> int:
    try:
        fail_num = int(input('失败尝试数(default 3)：'))
        return fail_num if fail_num > 0 else 3
    except:
        return 3

def get_max_save_num() -> int:
    try:
        save_num = int(input('备份文件数(default 5)：'))
        return save_num if save_num > 0 else 5
    except:
        return 5

def init():
    return '', 0, 0, 0

def main():
    cur_save_num = 1
    cur_fail_num = 0
    dir_name = opath.dirname(opath.abspath(__file__))
    config_path = dir_name + '\\config.ini'
    if not opath.exists(config_path):
        try:
            with open(config_path, 'w') as f: pass
        except Exception as e:
            print(e)
    save_path, alternate, fail_times, max_save_num = init()
    global_config.createInstance(config_path)   #创建配置文件实例
    try:
        if opath.getsize(config_path) == 0:
            save_path = get_path()
            make_path(save_path)
            alternate = get_stop_time()
            max_save_num = get_max_save_num()
            fail_times = get_max_fail_num()
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write('[psd]\nsave_path={}\nalternate={}\nmax_save_num={}\nfail_times={}\
                    \n'.format(save_path, alternate, max_save_num, fail_times))
        else:
            print('读取配置文件({})完毕.'.format(config_path))
            save_path = global_config.get('psd', 'save_path')
            alternate = int(global_config.get('psd', 'alternate'))
            fail_times = int(global_config.get('psd', 'fail_times'))
            max_save_num = int(global_config.get('psd', 'max_save_num'))
            make_path(save_path)
        system('cls')
        psd_path = save_path + 'default.psd'
        print('Saved full path is \"{}\".'.format(psd_path))
        print('Save period is {}s!'.format(alternate))
        print('Max fail times is {}.'.format(fail_times))
        print('Max save num is {}.\n'.format(max_save_num))
        #doc.fullname to get full path_name, but must save first
        while True:
            with Session() as ps:
                doc = ps.active_document
                options = ps.PhotoshopSaveOptions()
                layers = doc.artLayers
                #doc.save()#报错
                doc.saveAs(psd_path, options, True)

                if check_path(psd_path):
                    try:
                        real_tmp_name = str(doc.fullName).split('\\')[-1]
                        real_name = '.'.join(real_tmp_name.split('.')[0:-1]) + str(cur_save_num) + '.psd'
                        full_path = save_path + real_name
                        if opath.exists(full_path):
                            remove(full_path)
                        rename(psd_path, full_path)
                        if check_path(full_path):
                            print('{}保存成功.'.format(full_path))
                            cur_save_num += 1
                            if cur_save_num > max_save_num:
                                cur_save_num = 1
                        else:
                            print('{}保存成功.'.format(psd_path))
                    except:
                        pass
                else:
                    msg = '{}保存失败!'.format(psd_path)
                    if cur_fail_num >= fail_times:
                        msg += '脚本已退出。'
                        ps.alert(msg)
                        break
                    ps.alert(msg)
                    print(msg)
                    cur_fail_num += 1
            sleep(alternate)
    except Exception as e:
        print(e)
        system('pause')


if __name__ == '__main__':
    main()