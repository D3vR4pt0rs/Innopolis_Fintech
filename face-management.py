import cognitive_face as CF
from json import load
import cv2
import os
import sys
import argparse

trash = open('faceapi.json', 'r')
trsh = load(trash)
KEY = trsh['key']
BASE_URL = trsh['serviceUrl']
grid = trsh['groupId']
trash.close()

CF.Key.set(KEY)
CF.BaseUrl.set(BASE_URL)
path = os.getcwd() + '/frames/'


# создание директории для временных файлов
def make_dir_fr():
    try:
        os.rmdir(path)
    except:
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)
        except:
            pass
    os.mkdir(path)


# удаление директории, завершение работы программы
def end():
    try:
        os.rmdir(path)
    except:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
    sys.exit(0)


# создает 5 файлов ('frame'+ count +'.jpg', проверяет на наличие 5 лиц)
def get_frames(video):
    cap = cv2.VideoCapture(video)
    frames_count = 0
    ret, now_fr = cap.read()
    while ret:
        frames_count += 1
        ret, now_fr = cap.read()
    if frames_count < 5:
        print('Video does not contain any face')
        end()
    indexes = [0,
               int((frames_count - 1) / 4),
               int((frames_count - 1) / 2),
               int((frames_count - 1) * 3 / 4),
               int(frames_count - 1)]
    cap = cv2.VideoCapture(video)
    count = 0
    frames_count = 0
    ret, now_fr = cap.read()
    while ret:
        if frames_count == indexes[count]:
            cv2.imwrite(path + 'frame.jpg', now_fr)
            res = CF.face.detect(path + 'frame.jpg')
            if not res:
                print('Video does not contain any face')
                end()
            cv2.imwrite(path + 'frame' + str(count) + '.jpg', now_fr)
            count += 1
        frames_count += 1
        ret, now_fr = cap.read()


# US-004 Простое добавление пользователя в сервис индентификации
# sample-add
def einfache_Erganzung(video):
    make_dir_fr()
    get_frames(video)
    try:
        CF.person_group.create(grid)
    except:
        pass
    CF.person_group.update(grid, user_data='NeedTrain')
    res = CF.person.create(grid, 'id')['personId']
    print('5 frames extracted')
    print('PersonId:', res)
    print('FaceIds')
    print('=======')
    for i in range(5):
        print(CF.person.add_face(path + 'frame' + str(i) + '.jpg', grid, res)['persistedFaceId'])
    end()


# US-005 Улучшенное добавление пользователя в сервис индентификации
# add
def willkommen_zuruck(video1, video2, video3, video4, video5):
    pass


# US-006 Получение всех пользователей из сервиса идентификации
# list
def liste():
    try:
        li = CF.person.lists(grid)
        if len(li) == 0:
            print('No persons found')
        else:
            print('Persons IDs:')
            for i in li:
                print(i['personId'])
    except:
        print('The group does not exist')
    sys.exit(0)


# US-007 Удаление пользователя из сервиса идентификации
# del
def hinmachen(prid):
    try:
        CF.person.lists(grid)
    except:
        print("The group doesn't exist")
        sys.exit(0)
    try:
        CF.person.delete(grid,prid)
        CF.person_group.update(grid, user_data='NeedTrain')
        print('Person deleted')
    except:
        print("The person doesn't exist")
    sys.exit(0)


# US-008 Запуск обучения сервиса индентификации
# train
def trainieren():

    try:
        CF.person_group.get(grid)
    except:
        print('There is nothing to train')  # проверка на существование группы
        sys.exit(0)

    if not CF.person.lists(grid):
        print('There is nothing to train')  # проверка на наличие пользователей в группе
        sys.exit(0)

    if (CF.person_group.get(grid)['userData'] == 'NeedTrain') or (CF.person_group.get(grid)['userData'] is None):
        CF.person_group.train(grid)
        CF.person_group.update(grid, user_data='no')
        print('Training successfully started')
    else:
        print('Already trained')
    sys.exit(0)


# парсер
def key_to_value(args):
    if args.simple_add != " ":
        einfache_Erganzung(args.simple_add)
    if args.add != " ":
        willkommen_zuruck(args.add[0], args.add[1], args.add[2], args.add[3], args.add[4])
    if args.list != " ":
        liste()
    if args.delete != " ":
        hinmachen(args.delete)
    if args.train != " ":
        trainieren()


parser = argparse.ArgumentParser()
parser.add_argument('--simple-add', default=' ', nargs='?')
parser.add_argument('--add', default=' ', nargs='+')
parser.add_argument('--list', default=' ', nargs='?')
parser.add_argument('--delete', '-d', default=' ', nargs='?')
parser.add_argument('--train', default=' ', nargs='?')
parser.set_defaults(func=key_to_value)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)

