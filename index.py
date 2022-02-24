# -*- coding: utf-8 -*-
from cv2 import cv2

from captcha.solveCaptcha import solveCaptcha

from os import listdir
from src.logger import logger, loggerMapClicked
from random import randint
from random import random
import random as random2

import numpy as np
import mss
import pyautogui
import time
import sys
import array

import yaml


cat = """
                                                _
                                                \`*-.
                                                 )  _`-.
                                                .  : `. .
                                                : _   '  \\
                                                ; *` _.   `*-._
                                                `-.-'          `-.
                                                  ;       `       `.
                                                  :.       .        \\
                                                  . \  .   :   .-'   .
                                                  '  `+.;  ;  '      :
                                                  :  '  |    ;       ;-.
                                                  ; '   : :`-:     _.`* ;
                                               .*' /  .*' ; .*`- +'  `*'
                                               `*-*   `*-*  `*-*'
=========================================================================
================ Please, consider buying me an coffe :) =================
=========================================================================
============== 0xbd06182D8360FB7AC1B05e871e56c76372510dDf ===============
===== https://www.paypal.com/donate?hosted_button_id=JVYSC6ZYCNQQQ ======
=========================================================================

>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be fount in the config.yaml file."""


print(cat)


if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']
ch = c['home']
t = c['time_intervals']
interval_between_moviments = t['interval_between_moviments']

game_instances_count = c['instances']['count']

if not ch['enable']:
    print('>>---> Home feature not enabled')
print('\n')

pyautogui.PAUSE = interval_between_moviments

pyautogui.FAILSAFE = False
hero_clicks = 0
login_attempts = 0
last_log_is_progress = False


def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


def moveToWithRandomness(x, y, t):
    pyautogui.moveTo(addRandomness(x, 10), addRandomness(
        y, 10), round(random2.uniform(0.1, 0.4), 2))


def mouseClick():
    pyautogui.click()


def randomMouseMoviment():

    i = random2.randint(1, 100)
    r = random2.randint(300, 1000)
    t = round(random2.uniform(0.05, 0.2), 2)
    pyautogui.moveTo(r + i * 1.1, r - i * 1.1, t)


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


images = load_images()


def loadHeroesToSendHome():
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes


if ch['enable']:
    home_heroes = loadHeroesToSendHome()


def show(rectangles, img=None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)

def isVisible(img, threshold=ct['default'], printscreen = None):
    matches = positions(img, threshold=threshold, img=printscreen)
    return len(matches) != 0

def clickBtn(img, name=None, timeout=3, threshold=ct['default']):

    logger(None, progress_indicator=True)
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    clicked = False
    while (not clicked):
        matches = positions(img, threshold=threshold)
        if (len(matches) == 0):
            hast_timed_out = time.time()-start > timeout
            if (hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            time.sleep(0.05)
            continue

        x, y, w, h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x, pos_click_y, 1)
        mouseClick()
        return True

    return False


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = printSreen()

    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def scroll():

    commoms = positions(images['common-text'], threshold=ct['commom'])
    if (len(commoms) == 0):
        return
    x, y, w, h = commoms[len(commoms)-1]
#
    moveToWithRandomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'],
                          duration=0.70, button='left')


def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2), y+(h/2), 1)
        mouseClick()
        global hero_clicks
        hero_clicks = hero_clicks + 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)


def isHome(hero, buttons):
    y = hero[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
            return False
    return True


def isWorking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def clickGreenBarButtons():
    global hero_clicks

    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 140

    green_bars = positions(images['green-bar'], 0.85)
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' %
               len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2), y+(h/2), 1)
        mouseClick()
        
        hero_clicks = hero_clicks + 1

        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)


def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2), y+(h/2), 1)
        mouseClick()
        global hero_clicks
        hero_clicks = hero_clicks + 1

    return len(not_working_full_bars)


def goToHeroes():
    if clickBtn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    return clickBtn(images['hero-icon'])

def isHeroesTabOpen():
    return clickBtn(images['characters-stats'], timeout=30)

def goToGame():
    # in case of server overload popup
    clickBtn(images["x"], timeout=1)
    clickBtn(images["x"], timeout=1)
    clickBtn(images['treasure-hunt-icon'])


def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])
    clickBtn(images['treasure-hunt-icon'])

def gameIsOpen():
    img = printSreen()
    return (not len(positions(images['go-back-arrow'], img=img)) == 0) or (not len(positions(images['treasure-hunt-icon'])) == 0) or (not len(positions(images['x-2'])) == 0) or (not len(positions(images['new-map'], img=img)) == 0)

def acceptLoginTerms():
    if clickBtn(images['terms']):
        clickBtn(images['accept'])

def login(refresh = False):

    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 9:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        # pyautogui.hotkey('ctrl','f5')
        # return False

    if refresh:
        #pyautogui.hotkey("ctrl", "F5")
        #time.sleep(10)
        pass

    if clickBtn(images['unity'], timeout=5):
        pyautogui.hotkey("ctrl", "F5")
        time.sleep(5)

    acceptLoginTerms()

    if clickBtn(images['connect-wallet'], name='connectWalletBtn', timeout=30):
        login_attempts = login_attempts + 1
        logger('🎉 Connect wallet button detected, logging in!')
        # TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

        if clickBtn(images['metamask-bomb'], timeout=30) and clickBtn(images['select-wallet-2'], name='sign button', timeout=30):
            # sometimes the sign popup appears imediately
            login_attempts = login_attempts + 1
            # print('sign button clicked')
            # print('{} login attempt'.format(login_attempts))

            if clickBtn(images['error']) and clickBtn(images['ok']):
                return False

            if clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=60):
                # print('sucessfully login, treasure hunt btn clicked')
                login_attempts = 0
                return True
            else:
                return False
        else:
            if clickBtn(images["metamask_bar"], threshold=0.9):
            #if clickBtn(images["metamask_bar_w10"], threshold=0.9):
                if clickBtn(images['select-wallet-2'], name='sign button', timeout=30):

                    if clickBtn(images['error']) and clickBtn(images['ok']):
                        return False

                    if clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=30):
                        if not clickBtn(images['ok']):
                            return True
                    else:
                        return False

        if not clickBtn(images['select-wallet-1-no-hover'], name='selectMetamaskBtn'):
            if clickBtn(images['select-wallet-1-hover'], name='selectMetamaskHoverBtn', threshold=ct['select_wallet_buttons']):
                pass
                # o ideal era que ele alternasse entre checar cada um dos 2 por um tempo
                # print('sleep in case there is no metamask text removed')
                # time.sleep(20)
        else:
            pass
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)

        if clickBtn(images['select-wallet-2'], name='signBtn', timeout=30):
            login_attempts = login_attempts + 1
            # print('sign button clicked')
            # print('{} login attempt'.format(login_attempts))
            # time.sleep(25)
            if clickBtn(images['treasure-hunt-icon'], name='teasureHunt', timeout=30):
                # print('sucessfully login, treasure hunt btn clicked')
                login_attempts = 0
                return True
            # time.sleep(15)

        if clickBtn(images['ok'], name='okBtn'):
            return False
            # time.sleep(15)
            # print('ok button clicked')
        
        return True


def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len(hero_positions) == 0:
            # TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return

    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(
        images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(
        images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position, go_home_buttons):
            if not isWorking(position, go_work_buttons):
                print('hero not working, sending him home')
                moveToWithRandomness(
                    go_home_buttons[0][0] + go_home_buttons[0][2] / 2, position[1] + position[3] / 2, 1)
                mouseClick()
            else:
                print('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')

def sendHeroesToRest():

    logger('🏢 Search for heroes to work')

    global hero_clicks
    hero_clicks = 0

    if not goToHeroes():
        return False

    if not isHeroesTabOpen():
        return False

    clickBtn(images['all-rest'])

    goToGame()
    return True


def refreshHeroes():

    logger('🏢 Search for heroes to work')

    global hero_clicks
    hero_clicks = 0

    if not goToHeroes():
        return False

    if not isHeroesTabOpen():
        return False

    clickBtn(images['all-rest'], timeout=0.05)
    time.sleep(2.5)

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    for i in range(0, 5):

        if c['select_heroes_mode'] == 'full':
            clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            clickGreenBarButtons()
        else:
            clickButtons()

        sendHeroesHome()

        if i < 3:
            scroll()

        time.sleep(2.75)

    logger('💪 {} heroes sent to work'.format(hero_clicks))
    goToGame()
    return True


def checks(reset=False):

    printscreen = printSreen()

    if isVisible(images["error"], printscreen=printscreen):
        pyautogui.hotkey('ctrl', 'f5')
        time.sleep(15)
        return

    isVisible(images['new-map'], printscreen=printscreen)
    isVisible(images["ok"], printscreen=printscreen)
    isVisible(images["x"], printscreen=printscreen)
    isVisible(images["x-2"], printscreen=printscreen)
    isVisible(images["arrow-down"], printscreen=printscreen)
    isVisible(images['treasure-hunt-icon'], printscreen=printscreen)
    isVisible(images['new-map'], printscreen=printscreen)
    isVisible(images["ok"], printscreen=printscreen)
    isVisible(images["x"], printscreen=printscreen)
    isVisible(images["x-2"], printscreen=printscreen)
    isVisible(images["arrow-down"], printscreen=printscreen)
    isVisible(images['treasure-hunt-icon'], printscreen=printscreen)


def main():
    time.sleep(1 * 1 * 5)
    game_instances = []

    for i in range(0, game_instances_count):
        game_instances.append({
            "heroes": 0,
            "refresh_heroes": 0,
            "index": i + 1,
            "refresh_heroes_count": 0
        })

    while True:
        now = time.time()

        for i in range(0, game_instances_count):

            checks()

            any_action_taken = False
            logged_in = False

            if gameIsOpen() or login(True) == True:
                logged_in = True
                sys.stdout.flush()

            if logged_in == True:
                
                any_action_taken = True

                if now - game_instances[i]["heroes"] > t['send_heroes_for_work'] * 60:

                    if game_instances[i]["refresh_heroes_count"] > 5:
                        game_instances[i]["refresh_heroes_count"] = 0

                    if refreshHeroes():
                        game_instances[i]["heroes"] = now
                        game_instances[i]["refresh_heroes"] = now
                        game_instances[i]["refresh_heroes_count"] = game_instances[i]["refresh_heroes_count"] + 1
                        any_action_taken = True
                    else:
                        pass
                        #pyautogui.hotkey("ctrl", "F5")

                if now - game_instances[i]["refresh_heroes"] > t['refresh_heroes_positions'] * 60:
                    game_instances[i]["refresh_heroes"] = now
                    any_action_taken = True
                    refreshHeroesPositions()

            sys.stdout.flush()

            if any_action_taken is False or game_instances_count == 1:
                logger('5 minutes sleep')
                time.sleep(5 * 60)
            
            if game_instances_count > 1:
                logger("Changing to " +
                    str(game_instances[i]['index']) + " BombCrypto instance.")
            
                pyautogui.keyDown('alt')
                aux = game_instances_count
                while aux > 1:
                    pyautogui.press('tab')
                    aux = aux - 1
                    time.sleep(0.001)
                pyautogui.keyUp('alt')


exceptions = 100


def mainLoop():
    try:
        main()
    except Exception as error:

        logger(error, color="red")
        global exceptions
        exceptions = exceptions - 1

        if exceptions > 0:
            #pyautogui.hotkey('ctrl','f5')
            time.sleep(10)
            mainLoop()


if __name__ == '__main__':
    mainLoop()

# sendHeroesHome()


# cv2.imshow('img',sct_img)
# cv2.waitKey()

# chacar se tem o sign antes de aperta o connect wallet ?
# arrumar aquela parte do codigo copiado onde tem q checar o sign 2 vezes ?
# colocar o botao em pt
# melhorar o log
# salvar timestamp dos clickes em newmap em um arquivo
# soh resetar posiçoes se n tiver clickado em newmap em x segundos

# pegar o offset dinamicamente
# clickar so no q nao tao trabalhando pra evitar um loop infinito no final do scroll se ainda tiver um verdinho
# pip uninstall opencv-python

# pip install --upgrade opencv-python==4.5.3.56
