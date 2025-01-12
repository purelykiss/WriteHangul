# -*- coding: utf-8 -*-
import msvcrt
# 디버그 로그용
import logging

import unicodedata

from win32api import GetKeyState
from win32con import VK_NUMLOCK

LOG_FILENAME = 'pyime.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, )

# 키보드 영어 소문자 -> 한글자모 맵핑
lower_to_jm = [
    u"ㅁ", u"ㅠ", u"ㅊ", u"ㅇ", u"ㄷ", u"ㄹ", u"ㅎ", u"ㅗ", u"ㅑ", u"ㅓ",
    u"ㅏ", u"ㅣ", u"ㅡ", u"ㅜ", u"ㅐ", u"ㅔ", u"ㅂ", u"ㄱ", u"ㄴ", u"ㅅ",
    u"ㅕ", u"ㅍ", u"ㅈ", u"ㅌ", u"ㅛ", u"ㅋ"]
# 키보드 영어 대문자 -> 한글자모 맵핑
upper_to_jm = [
    u"ㅁ", u"ㅠ", u"ㅊ", u"ㅇ", u"ㄸ", u"ㄹ", u"ㅎ", u"ㅗ", u"ㅑ", u"ㅓ",
    u"K", u"ㅣ", u"ㅡ", u"ㅜ", u"ㅒ", u"ㅖ", u"ㅃ", u"ㄲ", u"ㄴ", u"ㅆ",
    u"ㅕ", u"ㅍ", u"ㅈ", u"ㅌ", "ㅛ", "ㅋ"]

# 초성,중성,종성 인덱스 맵핑
CHO_DATA = u"ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ";
JUNG_DATA = u"ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ";
# 종성의 맨 앞빈칸은 종성이 없는 글자의 표현
JONG_DATA = u" ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ";

# 보통 utf-8방식을 선호하나 커맨드창에 한글이 보이게 하기위해 cp949로 인코딩
ENCODING = 'utf-8'


def isascii(u):
    logging.debug("isascii u:%s %d", u.encode(ENCODING), (0 < ord(u) < 0xff))
    return (0 < ord(u) < 0xff)


def isprint(c):
    k = ord(c)
    return (0x20 <= k <= 0x40) or (0x7b <= k <= 0x7e) or \
        (0x41 <= k <= 0x5a) or (0x61 <= k <= 0x7a)


def get_capslock_state():
    return GetKeyState(VK_NUMLOCK) == 1


def is_jaum(u_jm):
    """키보드에서 입력된 자모가 자음인지 판단

        소스내에선 선별된 자모를 대상으로 하기때문에 자음이 아니면 모음

    @파라미터: u_jm: 유니코드 자모
    @반환: 자음이면 참, 모음이면 거짓
    """
    return u_jm in CHO_DATA


def engkey2kor(c):
    """영어키 변환

        영어문자1개 -> 한글자모로 맵핑하여 반환

    @파라미터: c: 타입은 스트링형, 변환하고자 하는 문자
    @반환: 영문자에 해당하는 자모, 영대소문자가 아니면 None
    """
    if c.islower():
        return lower_to_jm[ord(c) - 97]
    if c.isupper():
        return upper_to_jm[ord(c) - 65]
    return None


def asm(cho, jung, jong):
    """유니코드 알아내기

        초/중/종성으로 해당 글자의 유니코드를 얻어낸다.
        유니코드에서 한글 가~힝은 0xAC00~0xD7A3에 대응된다.
        이는 C언어 배열 3차원 배열로 표현할수 있다.
            예) unicode[19][21][28] 초성19,중성21,종성28 배열의 시작번지는 AC00
        따라서 초성 중성 종성의 값(인덱스값)을 알면 해당글자의 유니코드를 구할 수 있다.

    @파라미터: cho: 타입은 유니코드, 초성 코드
    @파라미터: jung: 타입은 유니코드, 중성 코드
    @파라미터: jong: 타입은 유니코드, 종성 코드
    @반환: 초+중+종에 해당하는 글자의 유니코드
    """
    dcho = cho.encode(ENCODING) if cho else "*None"
    djung = jung.encode(ENCODING) if jung else "*None"
    djong = jong.encode(ENCODING) if jong else "*None"
    if cho and not jung and not jong: return cho
    if not cho and jung: return jung
    idx_cho = CHO_DATA.find(cho)
    idx_jung = JUNG_DATA.find(jung)
    if jong:
        idx_jong = JONG_DATA.find(jong)
    else:
        idx_jong = 0
    return chr(idx_cho * 21 * 28 + idx_jung * 28 + idx_jong + 0xAC00)


def asm_jm(u_jm1, u_jm2):
    """이중자음/이중모음 유니코드 알아내기

        입력받은 두 자모를 합쳐서 이중모음 또는 이중자음의
        유니코드를 반환한다

    @파라미터: u_jm1: 타입은 유니코드,첫번째 자모
    @파라미터: u_jm2: 타입은 유니코드,두번째 자모
    @반환: 이중자모 유니코드 반환 , 해당자모가 없으면 None
    """
    if u_jm1 == u"ㅗ" and u_jm2 == u"ㅏ": return u"ㅘ"
    if u_jm1 == u"ㅗ" and u_jm2 == u"ㅐ": return u"ㅙ"
    if u_jm1 == u"ㅗ" and u_jm2 == u"ㅣ": return u"ㅚ"
    if u_jm1 == u"ㅜ" and u_jm2 == u"ㅓ": return u"ㅝ"
    if u_jm1 == u"ㅜ" and u_jm2 == u"ㅔ": return u"ㅞ"
    if u_jm1 == u"ㅜ" and u_jm2 == u"ㅣ": return u"ㅟ"
    if u_jm1 == u"ㅡ" and u_jm2 == u"ㅣ": return u"ㅢ"
    if u_jm1 == u"ㄱ" and u_jm2 == u"ㅅ": return u"ㄳ"
    if u_jm1 == u"ㄴ" and u_jm2 == u"ㅈ": return u"ㄵ"
    if u_jm1 == u"ㄴ" and u_jm2 == u"ㅎ": return u"ㄶ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㄱ": return u"ㄺ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㅁ": return u"ㄻ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㅂ": return u"ㄼ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㅅ": return u"ㄽ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㅍ": return u"ㄿ"
    if u_jm1 == u"ㄹ" and u_jm2 == u"ㅎ": return u"ㅀ"
    if u_jm1 == u"ㅂ" and u_jm2 == u"ㅅ": return u"ㅄ"
    return None


def ime_wprint(u_code, bs=0):
    """화면출력함수

        글자(1개)를 화면에 출력한다.
        두번째 인자는 백스페이스의 횟수를 지정한다
        딜폴트 값은 0으로 이는 이전에 출력되었던 글자를
        지우지 않겠다는 뜻이다. gotoxy(x,y)를 사용할 수 없는 환경이기때문에
        백스페이스를 이용하여 이전 글자를 지운다.
        이전 글자를 지우는 주요한 이유는 한글자를 조립하는 동안에
        현재커서의 진행을 막기 위함이다.

    @파라미터: u_code: 타입은 유니코드,출력하고자 하는 글자(1개)
    @파라미터: bs: 타입은 정수,백스페이스 횟수
               한 글자를 지우기 위해선 2회의 백스페이스를 지정해야 한다.
    """
    for i in range(bs):
        msvcrt.putwch(u"\b")

    if u_code:
        msvcrt.putwch(u_code)


"""
state: 현재의 글자조립상태

         (0)               : 초기상태    
          |                 
         (1)               : 초성입력 상태
          |
         (2) -> (3)        : 중성입력 상태 / 중성 이중모음 상태
          |
         (4) -> (5)        : 종성입력 상태 / 종성 이중자음 상태
"""
state = 0
# 현재 조립중인 초/중/종성 보관
cho = None
jung = None
jong = None
jung1 = None  # 이중모음 첫번째 모음
jung2 = None  # 이중모음 두번째 모음
jong1 = None  # 이중자음 첫번째 자음
jong2 = None  # 이중자음 두번째 자음
input_list = []
if __name__ == '__main__':
    print
    """   한영키 사용금지 (영문모드에서만 입력)
                한영변환 ---> number Lock Key"""
    while True:
        c = msvcrt.getch()
        # 넘버스크롤 락이 걸려있으면
        # 한글입력으로 판단
        if not get_capslock_state():
            jm = engkey2kor(c)
        else:
            # 영문입력으로 판단
            jm = None
        # 한글키 작동되면 비프음
        if ord(c) > 127:
            msvcrt.putch('\x07')
            continue
        # 엔터키 입력 받음
        if c == '\r':
            if state != 0:
                input_list.append(asm(cho, jung, jong))
            msvcrt.putch('\r')
            msvcrt.putch('\n')
            for uc in input_list:
                msvcrt.putwch(uc)
            msvcrt.putch('\r')
            msvcrt.putch('\n')
            input_list = []
            state = 0
            cho = None;
            jung = None;
            jong = None
            continue
        # 백스페이스 입력받음
        if c == '\b':
            if state == 0:
                # 이전글자 삭제
                # 상태0
                try:
                    last_u = input_list.pop()
                except IndexError as e:
                    last_u = None
                if last_u:
                    if isascii(last_u):
                        ime_wprint(u' ', 1)
                        msvcrt.putwch(u"\b")
                    else:
                        ime_wprint(u' ', 2)
                        msvcrt.putwch(u"\b")
            elif state == 1:
                # 초 초기화
                # 상태0
                state = 0
                cho = None
                msvcrt.putwch(u"\b")
                msvcrt.putwch(u"\b")
                msvcrt.putwch(u" ")
                msvcrt.putwch(u"\b")
            elif state == 2:
                # 상태 1
                # 중초기화
                state = 1
                jung = None;
                ime_wprint(asm(cho, jung, jong), 2)
            elif state == 3:
                # 상태2
                state = 2
                jung = jung1
                jung1 = None;
                jung2 = None
                ime_wprint(asm(cho, jung, jong), 2)
            elif state == 4:
                # 상태2
                # 종초기화
                state = 2
                jong = None
                ime_wprint(asm(cho, jung, jong), 2)
            elif state == 5:
                # 종1종2 초기화
                # 상태4
                # 상태2
                state = 4
                jong = jong1
                jung1 = None;
                jung2 = None
                ime_wprint(asm(cho, jung, jong), 2)
            continue

        if not jm:
            # 자모이외에 해당하는 문자가 입력 되었다
            # 기존에 조립하던 글자를 완성
            # 특수글자출력
            # 새로운 시작으로 넘어감
            if state != 0:
                input_list.append(asm(cho, jung, jong))
            if isprint(c):
                new_u = c.decode(ENCODING)
                ime_wprint(new_u)
                input_list.append(new_u)
            state = 0
            cho = None;
            jung = None;
            jong = None
            continue
        if state == 0:  # --------------- 시작상태
            if is_jaum(jm):
                cho = jm
                state = 1
                ime_wprint(asm(cho, jung, jong))
            else:
                cho = None
                jung = jm
                state = 2
                ime_wprint(asm(cho, jung, jong))
        elif state == 1:  # --------------- 초성만 완성된 상태
            if is_jaum(jm):  # 자음이 입력
                # 글자가 완성되었고
                # 화면에 완성된 글자를 출력하고
                # 다음 글자로 넘어가면서
                # 지금 입력된 글자는 시작이 되어야 한다.
                state = 1
                input_list.append(cho)
                cho = jm;
                jung = None;
                jong = None
                ime_wprint(asm(cho, jung, jong))
            else:
                # 모음이 입력됨
                jung = jm
                state = 2
                uc = asm(cho, jung, jong)
                ime_wprint(uc, 2)
        elif state == 2:  # --------------- 중성까지 입력된 상태
            if is_jaum(jm):
                if cho:
                    # 자음이 들어옴
                    # 화면에 완성된 글자를 출력하고
                    # 새로 들오온 글자는 자음이므로
                    # 상태는 4
                    # 종성은 새로들어온 글자할당
                    state = 4
                    jong = jm
                    ime_wprint(asm(cho, jung, jong), 2)
                else:
                    input_list.append(jung)
                    state = 1
                    cho = jm;
                    jung = None;
                    jong = None
                    ime_wprint(asm(cho, jung, jong), 2)
            else:
                # 모음이 들어옴
                new_jm = asm_jm(jung, jm)
                if new_jm:  # 이중모음 판별
                    state = 3
                    jung1 = jung;
                    jung2 = jm
                    jung = new_jm
                    ime_wprint(asm(cho, jung, jong), 2)
                else:  # 이중모음 x
                    # 새로운 글자가 완성되었고
                    # 화면에 완성된 글자를 출력하고
                    # 새로 들오온 글자는 모음이므로
                    # 상태는 2
                    # 초성은 없음
                    # 중성은 현재글자를 할당
                    input_list.append(asm(cho, jung, jong))
                    state = 2
                    cho = None;
                    jung = jm;
                    jong = None
                    ime_wprint(asm(cho, jung, jong))
        elif state == 3:  # --------------- 중성까지 이중모음이 입력된 상태
            if is_jaum(jm):
                if cho and asm(cho, jung, jm):  # 초+중+종으로 한글완성여부 판별
                    state = 4
                    jong = jm
                    ime_wprint(asm(cho, jung, jong), 2)
                else:
                    # 새로운 글자가 완성되었고
                    # 화면에완성된 글자를 출력하고
                    # 새로들어온 글자는 자음이므로
                    # 초성만 할당
                    # 상태는 1
                    input_list.append(jung)
                    state = 1
                    cho = jm;
                    jung = None;
                    jong = None
                    ime_wprint(asm(cho, jung, jong))
            else:
                # 새로운 글자가 완성되었고
                # 화면에 완성된 글자를 출력하고
                # 새로 들어온 글자는 모음이기 때문에
                # 상태는 2
                # 초성은 없음
                # 중성으 현재글자를 할당
                input_list.append(asm(cho, jung, jong))
                state = 2
                cho = None;
                jung = jm;
                jong = None
                ime_wprint(asm(cho, jung, jong))
        elif state == 4:  # --------------- 종성까지 입력된 상태
            if is_jaum(jm):
                new_jm = asm_jm(jong, jm)  # 종성의 이중자음 가능성 판별
                if new_jm and asm(cho, jung, jong):
                    # 화면에 완성된 글자를 출력하고
                    # 상태는 5
                    jong1 = jong;
                    jong2 = jm
                    jong = new_jm
                    ime_wprint(asm(cho, jung, jong), 2)
                    state = 5
                else:
                    # 새로운 글자가 완성되었고
                    # 화면에 완성된 글자를 출력하고
                    # 자음부터 시작
                    # 상태는 1
                    ime_wprint(asm(cho, jung, jong), 2)
                    input_list.append(asm(cho, jung, jong))
                    state = 1
                    cho = jm;
                    jung = None;
                    jong = None
                    ime_wprint(asm(cho, jung, jong))
            else:
                # 밍 상태에서 모음이 입력됨
                # 초성 중성으로 글자를 완성 하고
                # 종성 , 모음 -> 초성 중성으로 셋팅
                # 상태는 2로 만들어야 함
                ime_wprint(asm(cho, jung, None), 2)
                input_list.append(asm(cho, jung, None))
                state = 2
                cho = jong;
                jung = jm;
                jong = None
                ime_wprint(asm(cho, jung, jong))
        elif state == 5:  # --------------- 종성 이중자음까지 입력된 상태
            if is_jaum(jm):
                # 자음이 입력되었음
                # 기존글자는 그대로 두고
                # 새로입력된 자음으로 글자출력
                # 상태는 1
                input_list.append(asm(cho, jung, jong))
                cho = jm;
                jung = None;
                jong = None
                ime_wprint(asm(cho, jung, jong))
                state = 1
            else:
                # 모음이 입력되었음
                # 초,중,첫번째종성으로 새로운 글자완성 하여 화면에 출력
                # 종성마지막자음과 새로입력된 모음으로 초성중성을 완성
                # 상태는 2
                ime_wprint(asm(cho, jung, jong1), 2)
                input_list.append(asm(cho, jung, jong1))
                cho = jong2;
                jung = jm;
                jong = None
                ime_wprint(asm(cho, jung, jong))
                state = 2