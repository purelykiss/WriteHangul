import string
import keyboard
import winsound as ws
import ctypes

print("WriteHangul v1.1")
print("=" * 100)
print("사용법: 텍스트 커서를 원하는 곳에 위치하고, 우측 alt를 한번 누른 후, 원하는 말을 입력한다.")
print("다 입력했으면 다시 우측 alt를 누르면 지금까지 입력한 글이 한글로 텍스트 커서에 입력된다.")
print("Pause키나 cmd창을 닫아서 프로그램 종료")
print("=" * 100)

input_hangul = ''
activate_key = 'right alt'
flag_is_activate = False
flag_activate_sound = False

simbol_word = "`1234567890-=[]\\;\',./~!@#$%^&*()_+{}|:\"<>?"

no_shift_word = [
    "ㅁ", "ㅠ", "ㅊ", "ㅇ", "ㄷ", "ㄹ", "ㅎ", "ㅗ", "ㅑ", "ㅓ",
    "ㅏ", "ㅣ", "ㅡ", "ㅜ", "ㅐ", "ㅔ", "ㅂ", "ㄱ", "ㄴ", "ㅅ",
    "ㅕ", "ㅍ", "ㅈ", "ㅌ", "ㅛ", "ㅋ"]

shift_word = [
    "ㅁ", "ㅠ", "ㅊ", "ㅇ", "ㄸ", "ㄹ", "ㅎ", "ㅗ", "ㅑ", "ㅓ",
    "ㅏ", "ㅣ", "ㅡ", "ㅜ", "ㅒ", "ㅖ", "ㅃ", "ㄲ", "ㄴ", "ㅆ",
    "ㅕ", "ㅍ", "ㅉ", "ㅌ", "ㅛ", "ㅋ"]

CHO_DATA = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ";
JUNG_DATA = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ";
JONG_DATA = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ";

write_state = 0 #1:초성 2:초성1중성 3:초성1중성2 4:초성1중성1종성 5:초성1중성1종성2 6:초성1중성2종성 7:초성1중성2종성2 8:중성1 9:중성2
CHO_SUNG = None
JUNG_SUNG = None
JUNG_SUNG1 = None
JUNG_SUNG2 = None
JONG_SUNG = None
JONG_SUNG1 = None
JONG_SUNG2 = None

def asm_jm(u_jm1, u_jm2):
    """이중자음/이중모음 유니코드 알아내기

        입력받은 두 자모를 합쳐서 이중모음 또는 이중자음의
        유니코드를 반환한다

    @파라미터: u_jm1: 타입은 유니코드,첫번째 자모
    @파라미터: u_jm2: 타입은 유니코드,두번째 자모
    @반환: 이중자모 유니코드 반환 , 해당자모가 없으면 None
    """
    if u_jm1 == "ㅗ" and u_jm2 == "ㅏ": return "ㅘ"
    if u_jm1 == "ㅗ" and u_jm2 == "ㅐ": return "ㅙ"
    if u_jm1 == "ㅗ" and u_jm2 == "ㅣ": return "ㅚ"
    if u_jm1 == "ㅜ" and u_jm2 == "ㅓ": return "ㅝ"
    if u_jm1 == "ㅜ" and u_jm2 == "ㅔ": return "ㅞ"
    if u_jm1 == "ㅜ" and u_jm2 == "ㅣ": return "ㅟ"
    if u_jm1 == "ㅡ" and u_jm2 == "ㅣ": return "ㅢ"
    if u_jm1 == "ㄱ" and u_jm2 == "ㅅ": return "ㄳ"
    if u_jm1 == "ㄴ" and u_jm2 == "ㅈ": return "ㄵ"
    if u_jm1 == "ㄴ" and u_jm2 == "ㅎ": return "ㄶ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㄱ": return "ㄺ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㅁ": return "ㄻ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㅂ": return "ㄼ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㅅ": return "ㄽ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㅍ": return "ㄿ"
    if u_jm1 == "ㄹ" and u_jm2 == "ㅎ": return "ㅀ"
    if u_jm1 == "ㅂ" and u_jm2 == "ㅅ": return "ㅄ"
    return None

# 한글이 눌렸을 경우 add_hangul 호출
def press_hangul(key_name):
    try:
        tmp_num = ord(key_name) - ord("a")
        if tmp_num < 0: #key_name이 대문자일 경우
            tmp_num = ord(key_name) - ord("A")
        # shift 눌린 여부에 따라 작동
        if is_shift_pressed():
            str = shift_word[tmp_num]
        else:
            str = no_shift_word[tmp_num]
        # 입력된 한글에 따라 조합
        add_hangul(str)
    except Exception as e:
        print("press_hangul: 오류 발생")
        print("key_name: ", key_name)
        print("tmp_num: ", tmp_num)

# Shift 상태 확인
def is_shift_pressed():
    # Shift가 켜져있으면 1 아니면 0 리턴
    return ctypes.WinDLL("User32.dll").GetAsyncKeyState(0x10) < 0

# 내부 저장소에 한글 입력
def add_hangul(str):
    global write_state, CHO_SUNG, JUNG_SUNG, JUNG_SUNG1, JUNG_SUNG2, JONG_SUNG, JONG_SUNG1, JONG_SUNG2
    #글자 없을 때 입력
    if write_state == 0:
        if str in CHO_DATA:
            CHO_SUNG = str
            write_state = 1
        elif str in JUNG_DATA:
            JUNG_SUNG = str
            write_state = 8
    #초성1일 때 입력
    elif write_state == 1:
        if str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            write_state = 1
        elif str in JUNG_DATA:
            JUNG_SUNG1 = str
            JUNG_SUNG = str
            write_state = 2
    #초성1중성1일 때 입력
    elif write_state == 2:
        if str in JONG_DATA:
            JONG_SUNG1 = str
            JONG_SUNG = str
            write_state = 4
        if str in JUNG_DATA:
            JUNG_SUNG = asm_jm(JUNG_SUNG1,str)
            if JUNG_SUNG != None:
                JUNG_SUNG2 = str
                write_state = 3
            else:
                JONG_SUNG = JUNG_SUNG1
                add_a_word()
                CHO_SUNG = None
                JUNG_SUNG1 = str
                JUNG_SUNG = str
                write_state = 8
    #초성1중성2일 때 입력
    elif write_state == 3:
        if str in JONG_DATA:
            JONG_SUNG1 = str
            JONG_SUNG = str
            write_state = 6
        if str in JUNG_DATA:
            add_a_word()
            CHO_SUNG = None
            JUNG_SUNG1 = str
            JUNG_SUNG = str
            write_state = 8
    #초성1중성1종성1일 때 입력
    elif write_state == 4:
        if asm_jm(JONG_SUNG1, str) != None:
            JONG_SUNG2 = str
            JONG_SUNG = asm_jm(JONG_SUNG1, str)
            write_state = 5
        elif str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 1
        elif str in JUNG_DATA:
            tmp_CHO_SUNG = JONG_SUNG1
            JONG_SUNG = None
            JONG_SUNG1 = None
            add_a_word()
            CHO_SUNG = tmp_CHO_SUNG
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            write_state = 2
    #초성1중성1종성2일 때 입력
    elif write_state == 5:
        if str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 1
        elif str in JUNG_DATA:
            tmp_CHO_SUNG = JONG_SUNG2
            JONG_SUNG2 = None
            JONG_SUNG = JONG_SUNG1
            add_a_word()
            CHO_SUNG = tmp_CHO_SUNG
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 2
    #초성1중성2종성1일 때 입력
    elif write_state == 6:
        if asm_jm(JONG_SUNG1, str) != None:
            JUNG_SUNG2 = str
            JONG_SUNG = asm_jm(JONG_SUNG1, str)
            write_state = 7
        elif str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 1
        elif str in JUNG_DATA:
            tmp_CHO_SUNG = JONG_SUNG1
            JONG_SUNG = None
            JONG_SUNG1 = None
            add_a_word()
            CHO_SUNG = tmp_CHO_SUNG
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            write_state = 2
    #초성1중성2종성2일 때 입력
    elif write_state == 7:
        if str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 1
        elif str in JUNG_DATA:
            tmp_CHO_SUNG = JONG_SUNG2
            JONG_SUNG2 = None
            JONG_SUNG = JONG_SUNG1
            add_a_word()
            CHO_SUNG = tmp_CHO_SUNG
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            JONG_SUNG = None
            JONG_SUNG1 = None
            write_state = 2
    #중성1일 때 입력
    elif write_state == 8:
        if str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            write_state = 1
        elif asm_jm(JUNG_SUNG1, str) != None:
            JUNG_SUNG = asm_jm(JUNG_SUNG1, str)
            JUNG_SUNG2 = str
            write_state = 9
        elif str in JUNG_DATA:
            add_a_word()
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            #write_state = 8
    #중성2일 때 입력
    elif write_state == 9:
        if str in CHO_DATA:
            add_a_word()
            CHO_SUNG = str
            JUNG_SUNG = None
            JUNG_SUNG1 = None
            JUNG_SUNG2 = None
            write_state = 1
        elif str in JUNG_DATA:
            add_a_word()
            JUNG_SUNG = str
            JUNG_SUNG1 = str
            JUNG_SUNG2 = None
            write_state = 8    

def backspace_hangul():
    global input_hangul, write_state, CHO_SUNG, JUNG_SUNG, JUNG_SUNG1, JUNG_SUNG2, JONG_SUNG, JONG_SUNG1, JONG_SUNG2
    # 1:초성 2:초성1중성 3:초성1중성2 4:초성1중성1종성 5:초성1중성1종성2 6:초성1중성2종성 7:초성1중성2종성2 8:중성1 9:중성2
    #글자가 없을 때 백스페이스
    if write_state == 0:
        if len(input_hangul) > 0:
            input_hangul = input_hangul[0:-2]
    #초성1일 때 백스페이스
    elif write_state == 1:
        CHO_SUNG = None
        write_state = 0
    #초성1중성1일 때 백스페이스
    elif write_state == 2:
        JUNG_SUNG = None
        JUNG_SUNG1 = None
        write_state = 1
    #초성1중성2일 때 백스페이스
    elif write_state == 3:
        JUNG_SUNG = JUNG_SUNG1
        JUNG_SUNG2 = None
        write_state = 2
    #초성1중성1종성일 때 백스페이스
    elif write_state == 4:
        JONG_SUNG = None
        JONG_SUNG1 = None
        write_state = 2
    #초성1중성1종성2일 때 백스페이스
    elif write_state == 5:
        JONG_SUNG = JONG_SUNG1
        JONG_SUNG2 = None
        write_state = 4
    #초성1중성2종성일 때 백스페이스
    elif write_state == 6:
        JONG_SUNG = None
        JONG_SUNG1 = None
        write_state = 3
    #초성1중성2종성2일 때 백스페이스
    elif write_state == 7:
        JONG_SUNG = JONG_SUNG1
        JONG_SUNG2 = None
        write_state = 6
    #중성1일 때 백스페이스
    elif write_state == 8:
        JUNG_SUNG = None
        JUNG_SUNG1 = None
        write_state = 0
    #중성2일 때 백스페이스
    elif write_state == 9:
        JUNG_SUNG = JUNG_SUNG1
        JUNG_SUNG2 = None
        write_state = 8

def space_hangul():
    global input_hangul
    add_a_word()
    input_hangul += ' '
    initialize_word()

def simbol_hangul(str):
    global input_hangul
    add_a_word()
    input_hangul += str
    initialize_word()

# 한 글자 조합완료 >> input_hangul에 입력
def add_a_word():
    global input_hangul, CHO_SUNG, JUNG_SUNG, JONG_SUNG

    # cnt = CHO_SUNG not None + JUNG_SUNG1 not None + JUNG_SUNG2 not None + JONG_SUNG1 not None + JONG_SUNG2 not None
    # keyboard.write("\b" * cnt)

    # 입력중인 글자가 아예 없는 경우 메소드를 나옴
    if not CHO_SUNG and not JUNG_SUNG and not JONG_SUNG:
        return
    # 초성만 있는 경우 글자 추가
    elif CHO_SUNG and not JUNG_SUNG:
        input_hangul += CHO_SUNG
        return
    # 중성만 있는 경우 글자 추가
    elif not CHO_SUNG and JUNG_SUNG:
        input_hangul += JUNG_SUNG
        return JUNG_SUNG
    # 초성과 중성이 있는 경우 정리
    num_CHO_SUNG = CHO_DATA.find(CHO_SUNG)
    num_JUNG_SUNG = JUNG_DATA.find(JUNG_SUNG)
    #종성 처리
    if JONG_SUNG != None:
        num_JONG_SUNG = JONG_DATA.find(JONG_SUNG)
    else:
        num_JONG_SUNG = 0

    # 초성과 중성이 있는 경우 글자 추가
    try:
        new_word = chr((num_CHO_SUNG*588)+(num_JUNG_SUNG*28)+num_JONG_SUNG+44032)
        input_hangul += new_word
    except Exception as e:
        print(f"add_a_word : 예외발생, {e}")

# 조합 중인 글자 초기화
def initialize_word():
    global write_state, CHO_SUNG, JUNG_SUNG, JUNG_SUNG1, JUNG_SUNG2, JONG_SUNG, JONG_SUNG1, JONG_SUNG2
    write_state = 0
    CHO_SUNG = None
    JUNG_SUNG = None
    JUNG_SUNG1 = None
    JUNG_SUNG2 = None
    JONG_SUNG = None
    JONG_SUNG1 = None
    JONG_SUNG2 = None

# 최종 출력, 조합 중이던 한글도 input_hangul에 넣고 커서 위치로 input_hangul 내용 입력
def write_hangul():
    global input_hangul
    add_a_word()
    initialize_word()
    keyboard.write(input_hangul)
    input_hangul = ''
    keyboard.release("alt")

# 키 입력 감지
def on_key_event(event):
    global flag_activate_sound, activate_key, flag_is_activate, input_hangul
    # if event.event_type != 'down':
    #     keyboard.release("alt")
    #     return
    print("current key pressed: ", event.name, " ", event.scan_code)

    if not flag_is_activate and event.name != activate_key:
        #keyboard.release("alt")
        return

    #입력
    code = event.scan_code
    if(16 <= code <= 25) or (30 <= code <= 38) or (44 <= code <= 50):
        press_hangul(event.name) #a~z의 한자리 string 인수
    elif event.name == 'space':
        space_hangul()
    elif event.name == 'backspace':
        backspace_hangul()
    elif event.name in simbol_word:
        simbol_hangul(event.name)
        

    print("current input_hangul: ", input_hangul)

    if event.name == activate_key:
        flag_is_activate = not flag_is_activate
    if flag_is_activate:
        if not flag_activate_sound:
            ws.PlaySound("open.wav", ws.SND_ASYNC)
            flag_activate_sound = not flag_activate_sound
            #keyboard.press("alt")
    else:
        write_hangul()
        if flag_activate_sound:
            ws.PlaySound("close.wav", ws.SND_ASYNC)
            flag_activate_sound = not flag_activate_sound
            keyboard.release("alt")


# 전역적으로 키 이벤트를 감지
keyboard.on_press(on_key_event)

# 프로그램이 계속 실행되도록 유지
keyboard.wait('pause')  # Pause 키를 누르면 종료