from os import walk

import pygame.image


def import_folder(path):
    surface_list=[]
    for _,__,img_folder in walk(path):
        for img in img_folder:
            full_path=path+'/'+img
            img_surface=pygame.image.load(full_path).convert_alpha()
            surface_list.append(img_surface)
    return surface_list

def import_folder_disct(path):
    surf_disct={}

    for _,__,img_folder in walk(path):
        for img in img_folder:
            fullpath=path+'/'+img
            surf=pygame.image.load(fullpath).convert_alpha()
            surf_disct[img.split('.')[0]]=surf
    return surf_disct