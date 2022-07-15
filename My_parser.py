######################################################
# ------------------ Parameters -------------------- #
dataset_type = 0
'''
0 = aihub 도보영상
1 = aihub 표지판 신호등
2 = 셀렉트스타
3 = ETRI 신호등
'''
# blank_image_remain_ratio = 0.6  # image not contains any class
if_resize = True
imgsize = [640, 480]
ratio = [8,1,1]  # train/val/test
src_dir = 'C:/Users/dklee/Downloads/Aihub_pedestrian_sample/Bbox_1_new'
target_dir = 'C:/Users/dklee/Downloads/Aihub_pedestrian_sample/parsed'

########################################################

from PIL import Image
import os
import shutil
import random

def path_generator():
    dest=0
    total_score = sum(ratio)
    tmp = random.random()
    if(tmp < ratio[0]/total_score):
        path = target_dir+'/train'
        dest=0
    elif(tmp < (ratio[0]+ratio[1])/total_score):
        path = target_dir+'/val'
        dest=1
    else:
        path = target_dir+'/test'
        dest=2
    return [path, dest]  # dir_path & ENUM

def yaml_writer(nc, class_):
    with open(target_dir+"/data.yaml", 'w') as f:
        f.write("path: "+target_dir+"\ntrain: ./train/images\nval: ./val/images\n")
        f.write("test: ./test/images\n\nnc: %d\nnames: ["%nc)
        len_ = len(class_)
        for i in range(len_):
            f.write("'%s'"%class_[i])
            if(i<len_-1):
                f.write(', ')
            else:
                f.write(']')
        f.close()

def parser_0():
    folder_list = os.listdir(src_dir)
    for folder in folder_list:
        file_list = os.listdir(src_dir+'/'+folder)
        for file in file_list:
            if file.endswith(".xml"):
                xml = file
                break
        # for file in file_list:
        #     if file.endswith(".txt"):
        #         dumy = file
        #         break
        images = [file for file in file_list if file.endswith(".jpg")]
        # xml parsing
        nc=0
        classes={}
        train_val_test=[0,0,0]
        # print(src_dir+'/'+folder+'/'+xml)
        print("Processing %s..."%xml)
        with open(src_dir+'/'+folder+'/'+xml,'rt',encoding='UTF8') as f:
            lines = f.readlines()
            
            for i in range(len(lines)):
                line = lines[i]
                if "name" not in line or "username" in line or i<10:
                    continue
                # Classes
                if "id" not in line:
                    nc+=1
                    classes[line[line.find('<name>')+6 : line.find("</name>")]] = nc
                # Annotation
                else:
                    image_name = line[line.find('name=')+6 : line.find('.jpg')]
                    if(not os.path.exists(src_dir+'/'+folder+'/'+image_name+'.jpg')):
                        print(image_name+'.jpg  [Missing]')
                        continue
                    path = path_generator()
                    train_val_test[path[1]] += 1
                    width = float(line[line.find('width')+7 : line.find('height')-2])
                    height = float(line[line.find('height')+8 : line.find('>')-1])
                    with open(path[0]+'/labels/'+image_name+'.txt', 'w') as t:
                        while (1):
                            i=i+1
                            if("</image>" in lines[i]):
                                break
                            src = lines[i]
                            # print(src)
                            obj = src[src.find('label')+7 : src.find('occ')-2]
                            xtl = float(src[src.find('xtl')+5 : src.find('ytl')-2])
                            ytl = float(src[src.find('ytl')+5 : src.find('xbr')-2])
                            xbr = float(src[src.find('xbr')+5 : src.find('ybr')-2])
                            ybr = float(src[src.find('ybr')+5 : src.find('z_order')-2])
                            parsing = str(classes[obj])+' '+str((xbr+xtl)/2/width)+' '+str((ybr+ytl)/2/height)+' '+str((xbr-xtl)/width)+' '+str((ybr-ytl)/height)+'\n'
                            t.write(parsing)
                            i=i+1
                        t.close()


                    img = Image.open(src_dir+'/'+folder+'/'+image_name+'.jpg')
                    if(if_resize):
                        image_resize = img.resize((640,480))
                        image_resize.save(path[0]+'/images/'+image_name+'.jpg')
                    else:
                        img.save(path[0]+'/images/'+image_name+'.jpg')

    # Write data.yaml
    yaml_writer(nc, list(classes.keys()))
    print("Processed numbers of dataset = Train: %d, Val: %d, Test: %d"%(train_val_test[0],
        train_val_test[1], train_val_test[2]))
    return

def parser_1():
    return

def parser_2():
    return

def parser_3():
    return


def main():
    if os.path.exists(target_dir):
        if(len(os.listdir(target_dir))>0):
            ans = input("타겟 폴더 내부에 파일이 있습니다. 전부 지우고 계속 하시겠습니까? [y,n] : ")
            if(ans!='y'):
                return
            shutil.rmtree(target_dir)
            os.mkdir(target_dir)
    else:
        os.mkdir(target_dir)

    dir_list = ['train','train/images','train/labels','val','val/images','val/labels',
        'test','test/images','test/labels']
    for tmp in dir_list:
        os.mkdir(target_dir+'/'+tmp)

    if(dataset_type==0):
        parser_0()
    elif(dataset_type==1):
        parser_1()
    elif(dataset_type==2):
        parser_2()
    elif(dataset_type==3):
        parser_3()
    else:
        print("Wrong dataset_type value")

if __name__ == "__main__":
    main()
