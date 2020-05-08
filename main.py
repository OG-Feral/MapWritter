import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import sys
import requests


def create_keyboard2():
    keyboard = vk_api.keyboard.VkKeyboard(one_time=True)

    keyboard.add_button("Город", color=vk_api.keyboard.VkKeyboardColor.PRIMARY)
    keyboard.add_button("Страна", color=vk_api.keyboard.VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def create_keyboard3():
    keyboard = vk_api.keyboard.VkKeyboard(one_time=True)

    keyboard.add_button("Схема", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_button("Спутник", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    keyboard.add_button("Гибрид", color=vk_api.keyboard.VkKeyboardColor.POSITIVE)
    return keyboard.get_keyboard()


def map(scale, var, place):
    geocoder_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json")
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"][
            "found"] == "0":
            return 0
        else:
            h = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]['pos']
            t = h.replace(" ", ",")
            u = h.replace(" ", "%2C")
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    response = None
    map_request = f"https://static-maps.yandex.ru/1.x/?ll={t}&spn={scale}&l={var}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    return [map_file, u]

def main():
    vk_session = vk_api.VkApi(
        token="1b9f13f8f6a4774f3a127b91b4b69fb702502c6621aeea2778fdcead8f53b1740b685cd77edb7b36359a8")

    longpoll = VkBotLongPoll(vk_session, 194957994)
    f1 = True
    f2 = False
    f3 = False
    f4 = False
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event)
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            l = event.obj.message['text'].lower()
            if f1:
                if l == "начать":
                    keyboard1 = create_keyboard2()
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                    message="Выберите масштаб (Город, Страна)",
                                    random_id=random.randint(0, 2 ** 64), keyboard=keyboard1)
                    f1 = False
                    f2 = True
                    continue
                else:
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                    message="Напишите Начать для работы с ботом",
                                    random_id=random.randint(0, 2 ** 64))

            if f2:
                keyboard2 = create_keyboard3()
                if l == "город":
                    scale = "0.5,0.5"
                    val = "8"
                elif l == "страна":
                    scale = "12,12"
                    val = "5.5"
                else:
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Выберите масштаб (Город, Страна)",
                                     random_id=random.randint(0, 2 ** 64), keyboard=keyboard1)
                    continue
                vk = vk_session.get_api()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                message="Вид карты (Схема, Спутник, Гибрид)",
                                random_id=random.randint(0, 2 ** 64), keyboard=keyboard2)
                f2 = False
                f3 = True
                continue

            if f3:
                if l == "схема":
                    var = 'map'
                elif l == "спутник":
                    var = "sat"
                elif l == "гибрид":
                    var = "sat,skl"
                else:
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Вид карты (Схема, Спутник, Гибрид)",
                                     random_id=random.randint(0, 2 ** 64), keyboard=keyboard2)
                    continue
                vk = vk_session.get_api()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                message="Введите название места",
                                random_id=random.randint(0, 2 ** 64))
                f3 = False
                f4 = True
                continue

            if f4:
                place = event.obj.message['text']
                img = map(scale, var, place)
                if img == 0:
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     random_id=random.randint(0, 2 ** 64),
                                     message=f"Ошибка \nПопробуйте еще раз")
                else:
                    upload = vk_api.VkUpload(vk_session)
                    photo = upload.photo_messages(img[0], event.obj.message['from_id'])
                    vk_photo_id = f"photo{(photo[0]['owner_id'])}_{photo[0]['id']}"
                    print(photo[0]['owner_id'])
                    print(photo, vk_photo_id, sep="\n")
                    link = f"https://yandex.ru/maps/?ll={img[1]}&z={val}"
                    vk = vk_session.get_api()
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                    random_id=random.randint(0, 2 ** 64),
                                    message=f"Для подробной информации перейдите по ссылке\n{link}",
                                    attachment=vk_photo_id)
                    f1 = True
                    f4 = False


if __name__ == '__main__':
    main()
