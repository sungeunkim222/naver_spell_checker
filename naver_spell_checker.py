from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import json
import os
import datetime
import time
import re # 한글이 포함된지 확인하는 함수
import random
from diff_match_patch import diff_match_patch

correction_dict = {
    "안내 로봇": "안내로봇",
    "배송 로봇": "배송로봇",
    "청소 로봇": "청소로봇",
    "서빙 로봇": "서빙로봇",
    "물류 로봇": "물류로봇",
    "1층 1층": "1층",
    "로봇 0": "로봇0",
    "로봇 1": "로봇1",
    "PASSWORD 신": "PASSWORD 씬", #"신발"단어있어서 '신'->'씬'으로 바꾸면안됨.
    "PASSWORD신": "PASSWORD 씬",
    "씬설정": "씬 설정",
    "이 동": " 이동",
    "멀티비 전": "멀티비전",
    "배송해": "배송",
    "캔 티": "캔틴",
    "캔티": "캔틴",
    "캔 팀": "캔틴",
    "캔팀": "캔틴",
    "켄틴": "캔틴",
    "수취상": "수취장",
    "수취짱": "수취장",
    "수 췌장": "수취장",
    "전 재소": "적재소",
    "적재 소": "적재소",
    "적재쇼": "적재소",
    "배송 품": "배송품",
    "배 송품": "배송품",
    "차던 봉": "차단봉",
    "감자후": "감지 후",
    "자키": "작키",
    "총 전선": "충전선",
    "솔 링크": "솔링크",
    "충전돼": "충전대",
    "충전 배": "충전대",
    "분 기": "분기",
    "확인분기": "확인 분기",
    "의료용품 범": "의료용품점",
    "의료용품점로": "의료용품점으로",
    "초음파 실": "초음파실",
    "총 돌": "총돌",
    "수행장": "주행장",
    "장애 몰": "장애물",
    "퇴식 구": "퇴식구",
    "중들": "충돌",
    "상 차하는": "상차하는",
    "확인서": "확인소",
    "브리디": "브이디",
    "충전 독": "충전독",
    " 어로": "으로",
    "다 로봇": "타로봇",
    "구간구간": "구간",
    "발생했음에로": "발생했음으로",
    "두 번 재": "두 번째",
    "로우": "로",
    "수취쇼": "수취소",
    "수어 취소": "수취소",
    "타인 아웃": "타임아웃",
    "": "",
    "  ": " ",
}


# 한글이 포함된지 확인하는 함수
def contains_korean(value):
    return bool(re.search(r'[가-힣]', value))


def check_and_write_string(file_path, string_to_check):
    """
    파일에서 특정 문자열을 검색하고, 없으면 해당 문자열을 파일에 추가합니다.

    :param file_path: 파일 경로
    :param string_to_check: 파일에서 검색할 한글 문자열
    """
    # 파일이 없으면 빈 파일 생성
    if not os.path.exists(file_path+".txt"):
        print(f"'{file_path}' 파일이 존재하지 않아 빈 파일을 생성합니다.")
        with open(file_path+".txt", 'w', encoding='utf-8') as file:
            pass

    # 파일 읽기 (줄 단위)
    with open(file_path+".txt", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    string_to_check = remove_numbers_before_units(string_to_check)
    # 문자열이 파일에 없는 경우 추가
    if string_to_check + '\n' not in lines:
        #print(f"'{string_to_check}' 문자열이 파일에 없습니다. 추가합니다.")
        #print(string_to_check)
        with open(file_path+".txt", 'a', encoding='utf-8') as file:
            file.write(string_to_check + '\n')
    #else:
        #print(f"'{string_to_check}' 문자열이 이미 파일에 존재합니다.")


def remove_numbers_before_units(text):
    """
    문자열에서 '분', '초', '%' 앞의 숫자만 제거합니다.

    :param text: 입력 문자열
    :return: 변환된 문자열
    """
    # '분', '초', '%' 앞의 숫자를 제거하는 정규식
    result = re.sub(r'\d+(?=(회|일|시|분|초|%))', '', text)
    #배터리 부족으로 '일' 중단 에러_안내5
    return result




# 재귀적으로 JSON 객체의 문자열을 교정
def recursive_correct(obj, file):
    
    if isinstance(obj, dict):
        return {key: recursive_correct(value, file) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [recursive_correct(item, file) for item in obj]
    elif isinstance(obj, str):
        if contains_korean(obj): #한글이 포함되었다라면
                
            #txt파일에 중복값 확인 후 저장
            check_and_write_string(file + "_1중복체크", obj)
    else:
        return obj
    
###3. 재교정###
def reCorrection(file):
    file_path = file + "_2맞춤법교정"#교정된 파일
    with open(file_path+".txt", 'r', encoding='utf-8') as file1:
        lines_spel = file1.readlines()

    file_path = file + "_3재교정"
    # 파일이 없으면 빈 파일 생성
    if not os.path.exists(file_path+".txt"):
        print(f"'{file_path}' 파일이 존재하지 않아 빈 파일을 생성합니다.")
    with open(file_path+".txt", 'w', encoding='utf-8') as file1:
        pass
    for i in range(0, len(lines_spel), 3):
        before_sentence = lines_spel[i].replace("\n", "")
        after_sentence = lines_spel[i+1].replace("\n", "")
        #고유명사는 원래대로
        for wrong, correct in correction_dict.items():
            after_sentence = after_sentence.replace(wrong, correct)

        #교정된 경우에만 저장.
        if before_sentence != after_sentence:
            # 파일 읽기 (줄 단위)
            with open(file_path+".txt", 'r', encoding='utf-8') as file2:
                lines = file2.readlines()
            # 문자열이 파일에 없는 경우 추가
            if after_sentence + '\n' not in lines:
                #print(f"'{string_to_check}' 문자열이 파일에 없습니다. 추가합니다.")
                #print(string_to_check)
                with open(file_path+".txt", 'a', encoding='utf-8') as file3:
                    file3.write(before_sentence + '\n') 
                    file3.write(after_sentence + '\n\n')

# 4. 필드 에러 - 재귀적으로 JSON 객체의 문자열을 탐색
def field_recursive_error_counter(obj, file, keys=None):
    global field_error_count
    global korean_count
    global korean_error_count
    global isError

    if keys is None:
        keys = []
        
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_keys = keys + [key]
            field_recursive_error_counter(value, file, new_keys)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            field_recursive_error_counter(item, file, keys)
    elif isinstance(obj, str):
        if contains_korean(obj):  # 한글이 포함되었다면
            file_path = file + "_3재교정"#재교정된 파일
            with open(file_path+".txt", 'r', encoding='utf-8') as file1:
                lines_spel = file1.readlines()
            origin_no_number_str = remove_numbers_before_units(obj) #숫자제거
            korean_count += 1
            for i in range(0, len(lines_spel), 3):
                line = lines_spel[i].replace("\n", "")
 

                if line == origin_no_number_str:
                    before = lines_spel[i].replace("\n", "")
                    after = lines_spel[i+1].replace("\n", "")

                    isError = True
                    korean_error_count += 1
                    #print(file)
                    #print(lines[i])
                    #print(lines[i+1])
                    dmp = diff_match_patch()
                    diff = dmp.diff_main(before, after)
                    dmp.diff_cleanupSemantic(diff)
                    
##                        print("="*20)
##                        for j in range(len(diff)):
##                            print(diff[j])
                    """
                    안내대기소 -> 안내 대기소
                    (0, '안내')
                    (1, ' ')
                    (0, '대기소로 이동 중')

                    """

                    for j in range(len(diff)):

                        try:
                            if diff[j][0] == 0:
                                continue
                            
                            #변경된 경우는 검사했으니 넘어감
                            elif diff[j-1][0] == -1 and diff[j][0] == 1 and diff[j+1][0] == 0:
                                continue
                            
                            #추가만된 경우
                            elif diff[j-1][0] == 0 and diff[j][0] == 1 and diff[j+1][0] == 0: 
                                if diff[j-1][1][-1] == " ":
                                    if len(diff[j-1][1]) == 1: #앞글자가 띄어쓰기만 있는 경우
                                        a = diff[j-2][1].split()[-1] + " "
                                    else:
                                        a = diff[j-1][1].split()[-1] + " "
                                else:
                                    a = diff[j-1][1].split()[-1]
                                b = diff[j][1]
                                if diff[j+1][1][0] == " ":
                                    c = " " + diff[j+1][1].split()[0].replace("\n", "")
                                elif diff[j+1][1][0] == "\n":
                                    c = ""
                                else:
                                    c = diff[j+1][1].split()[0].replace("\n", "")
                                change_sentence = (a + c + " -> " + a + b + c).replace("'", "")
                                if change_sentence not in changeSentenceList:
                                    changeSentenceList.append(change_sentence)
                                    #print(change_sentence)
                                
                            #삭제만된  경우
                            elif diff[j-1][0] == 0 and diff[j][0] == -1 and diff[j+1][0] == 0: 
                                if diff[j-1][1][-1] == " ":
                                    a = diff[j-1][1].split()[-1] + " "
                                else:
                                    a = diff[j-1][1].split()[-1]
                                b = diff[j][1]
                                if diff[j+1][1][0] == " ":
                                    #print(j)
                                    if len(diff[j+1][1]) == 1: #뒷글자가 띄어쓰기만 있는 경우
                                        c = " " + diff[j+2][1].split()[0].replace("\n", "")
                                    else:
                                        c = " " + diff[j+1][1].split()[0].replace("\n", "")
                                elif diff[j+1][1][0] == "\n":
                                    c = ""
                                else:
                                    c = diff[j+1][1].split()[0].replace("\n", "")
                                change_sentence = (a + b + c + " -> " + a + c).replace("'", "")
                                if change_sentence not in changeSentenceList:
                                    changeSentenceList.append(change_sentence)
                                    #print(change_sentence)

                            #변경만된 경우
                            elif diff[j-1][0] == 0 and diff[j][0] == -1 and diff[j+1][0] == 1 and diff[j+2][0] == 0:
                                if diff[j-1][1][-1] == " ":
                                    a = diff[j-1][1].split()[-1] + " "
                                else:
                                    a = diff[j-1][1].split()[-1]
                                b = diff[j][1]
                                c = diff[j+1][1]
                                if diff[j+2][1][0] == " ":
                                    d = " " + diff[j+2][1].split()[0].replace("\n", "")
                                elif diff[j+2][1][0] == "\n":
                                    d = ""
                                else:
                                    d = diff[j+2][1].split()[0].replace("\n", "")
                                change_sentence = (a + b + d + " -> " + a + c + d).replace("'", "")
                                if change_sentence not in changeSentenceList:
                                    changeSentenceList.append(change_sentence)
                                    #print(change_sentence)

                            elif change_sentence != "":
                                change_sentence = ""
                                save_and_print(f"{j}번째 추출불가!")
                                save_and_print("="*20)
                                for j in range(len(diff)):
                                    save_and_print(diff[j])
                                continue
                        except:
                            change_sentence = ""
                            save_and_print(f"{j}번째 예외처리발생!")
                            save_and_print("="*20)
                            for j in range(len(diff)):
                                save_and_print(diff[j])
                            pass
                        
                        field = "->".join(keys) + " : " + change_sentence
                        #print(field)
                        if field in data_dict:
                            data_dict[field] += 1
                            field_error_count += 1
                            total_field_dict[field] += 1
                        else:
                            data_dict[field] = 1
                            total_field_dict[field] = 1
                            field_error_count += 1
                                
# 5. 결합 - 원본이랑 교정된 거랑 비교해서 완성해서 반환
def combination_recursive(obj, file):
    global isError
    global korean_count
    global korean_error_count
    
    if isinstance(obj, dict):
        return {key: combination_recursive(value, file) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [combination_recursive(item, file) for item in obj]
    elif isinstance(obj, str):
        if contains_korean(obj): #한글이 포함되었다라면
            korean_count += 1
            origin_no_number_str = remove_numbers_before_units(obj) #숫자제거

            file_path = file + "_3재교정"#교정된 파일
            with open(file_path+".txt", 'r', encoding='utf-8') as file1:
                lines_spel = file1.readlines()
                
            for i in range(0, len(lines_spel), 3):
                before_sentence = lines_spel[i].replace("\n", "")
                if origin_no_number_str == before_sentence:
                    spelling_no_number_str = lines_spel[i+1].replace("\n", "")
                        
                    # 숫자 추출을 위한 정규식
                    try:
                        obstacle = re.search(r'장애물 (\d+)회', obj).group(1)  # '회' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace("장애물 회", f"장애물 {obstacle}회")
                    except:
                        pass
                    
                    try:
                        collision = re.search(r'충돌 발생 (\d+)회', obj).group(1)  # '회' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace("충돌 발생 회", f"충돌 발생 {collision}회")
                    except:
                        pass
                    
                    try:
                        day = re.search(r'(\d+)일', obj).group(1)  # '일' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace(" 일 ", f" {day}일 ")
                    except:
                        try:
                            day = re.search(r'(\d+)일', obj).group(1)  # '일' 앞의 숫자 추출
                            spelling_no_number_str = spelling_no_number_str.replace("일", f"{day}일")
                        except:
                            pass
                    
                    try:
                        hour = re.search(r'(\d+)시간', obj).group(1)  # '시' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace(" 시간", f" {hour}시간")
                    except:
                        try:
                            hour = re.search(r'(\d+)시', obj).group(1)  # '시' 앞의 숫자 추출
                            spelling_no_number_str = spelling_no_number_str.replace(" 시 ", f" {hour}시 ")
                        except:
                            pass
                    
                    try:
                        minutes = re.search(r'(\d+)분', obj).group(1)  # '분' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace(" 분 ", f" {minutes}분 ")
                    except:
                        pass
                    
                    try:
                        seconds = re.search(r'(\d+)초가', obj).group(1)  # '초' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace(" 초가 ", f" {seconds}초가 ")
                    except:
                        try:
                            seconds = re.search(r'(\d+)초', obj).group(1)
                            spelling_no_number_str = spellㅐing_no_number_str.replace(" 초 ", f" {seconds}초 ")
                        except:
                            pass
                    
                    try:
                        battery = re.search(r'(\d+)%', obj).group(1)  # '%' 앞의 숫자 추출
                        spelling_no_number_str = spelling_no_number_str.replace("%", f"{battery}%")
                    except:
                        pass
                    #print(obj)
                    #print(spelling_no_number_str)
                    spelling_no_number_str = spelling_no_number_str.replace("\n", "")
                                

                        
                    #에러 카운트
                    if spelling_no_number_str != obj: ##원본이랑 수정된거랑 다르다면
                        isError =True
                        korean_error_count += 1
                        
                        file_path = file + "_4결합"
                        with open(file_path+".txt", 'a', encoding='utf-8') as file4:
                            file4.write(obj + '\n') 
                            file4.write(spelling_no_number_str + '\n\n')
                        
                    return spelling_no_number_str
            else:
                return obj
        else:
            return obj

    else:
        return obj

    
def save_and_print(text, filename = "output.txt"):
    """
    문자열을 텍스트 파일에 저장하고 콘솔에 출력합니다.
    
    Args:
        text (str): 저장 및 출력할 문자열
        filename (str): 저장할 파일 이름 (기본값: output.txt)
    """
    text = str(text)
    # 텍스트 파일에 저장
    with open(filename, "a", encoding="utf-8") as file:
        file.write(text + "\n")
    
    # 콘솔에 출력
    print(text)

data_count = 0
isError = False
data_error_count = 0
total_data_count = 0
total_data_error_count = 0

korean_count = 0
korean_error_count = 0
total_korean_count = 0
total_korean_error_count = 0

naver_count = 0
total_naver_count = 0
total_time = 0
total_start = time.time() # 시작

data_dict = {} # 필드 에러 딕셔너리 초기화
total_field_dict = {}
changeSentenceList = []
field_error_count = 0
total_field_error_count = 0

###크롬 드라이버 실행###
dv = webdriver.Chrome()
dv.get("http://www.naver.com")
elem = dv.find_element("id", "query")#검색
elem.send_keys("맞춤법 검사기")
elem.send_keys(Keys.RETURN)
time.sleep(2) #페이지가 넘어간다음에 검사할내용을 넣을 칸을 찾아야하는 시간이 필요함.
###크롬 드라이버 끝###

start = time.time() # 시작

if __name__ == "__main__":
    files = [f for f in os.listdir() if f.endswith('.json')]
    #print(files)
    if not files:
        print("현재 폴더에 JSON 파일이 없습니다.")
    save_and_print("===================시작==================")
    save_and_print(datetime.datetime.now())
    files_size = len(files)
    for i in range(len(files)):
        start = time.time() # 시작
        data_count = 0
        data_error_count = 0
        korean_count = 0
        korean_error_count = 0
        naver_count = 0
        
        file = files[i]
        print(file)

        json_datas = json.load(open(file, 'r', encoding='utf-8'))  # 파일 내용을 JSON 형식으로 로드
        size = len(json_datas)
        
       ###1. 중복체크 시작###
        j = 0 #데이터 카운트
        for json_data in json_datas[j:]:
            data_count += 1
            if (j+1)%1000 == 0:
                sec = time.time()-start # 종료 - 시작 (걸린 시간)
                sec2 = time.time() - total_start
                times = str(datetime.timedelta(seconds = sec)) # 걸린시간 보기좋게 바꾸기
                times2 = str(datetime.timedelta(seconds = sec2)) # 걸린시간 보기좋게 바꾸기
                short = times.split(".")[0] # 초 단위 까지만
                short2 = times2.split(".")[0] # 초 단위 까지만
                print(f"[{i+1}/{files_size}]-1. 중복체크 {file} {j+1}/{size}. {short} sec. {short2} sec.")
            corrected_data = recursive_correct(json_data, file) #딕셔니리
            j += 1
        ###1. 중복체크 끝###

        ###2. 맞춤법 검사기 시작###
        # 파일 읽기 (줄 단위)
        file_path = file + "_1중복체크"
        with open(file_path+".txt", 'r', encoding='utf-8') as file1:
            lines = file1.readlines()
            # 파일이 없으면 빈 파일 생성
        # 파일 생성_네이버 맞춤법 검사기 적용후 저장할 파일.
        #print(file, type(file))
        file_path = file + "_2맞춤법교정"
        if not os.path.exists(file_path+".txt"):
            print(f"'{file_path}' 파일이 존재하지 않아 빈 파일을 생성합니다.")
            with open(file_path+".txt", 'w', encoding='utf-8') as file2:
                pass

        size = len(lines)
        j = 0
        for line in lines:
            naver_count += 1
            sec = time.time()-start # 종료 - 시작 (걸린 시간)
            sec2 = time.time() - total_start
            times = str(datetime.timedelta(seconds = sec)) # 걸린시간 보기좋게 바꾸기
            times2 = str(datetime.timedelta(seconds = sec2)) # 걸린시간 보기좋게 바꾸기
            short = times.split(".")[0] # 초 단위 까지만
            short2 = times2.split(".")[0] # 초 단위 까지만
            print(f"[{i+1}/{files_size}]-2. 맞춤법검사 {file} {j+1}/{size}, {short} sec, {short2} sec")
            line = line.replace('\n', '')
            #맞춤법 검사할 내용
            elem = dv.find_element(By.CLASS_NAME, "txt_gray")
            elem.send_keys(line)

            #검사 버튼
            elem = dv.find_element(By.CLASS_NAME, "btn_check")
            elem.click()
            time.sleep(1) # 너무빨리 결과같은 추출하면 검사중이라서 이상한 값이 추출됨.

            soup = BeautifulSoup(dv.page_source, 'html.parser')
            kospacing_sent = soup.select("p._result_text.stand_txt")[0].text
                
            if line != kospacing_sent:
                #print(line)
                #print(kospacing_sent + "\n")
            
                with open(file_path+".txt", 'a', encoding='utf-8') as file3:
                    file3.write(line + "\n")
                    file3.write(kospacing_sent + "\n\n")

            #맞춤법 검사할 내용
            elem = dv.find_element(By.CLASS_NAME, "stand_txt") # 다음문장은 클래스 이름이 바뀜.
            elem.clear() # 제거
            j += 1
        ###2. 맞춤법검사기 끝###

        #3. 재교정
        reCorrection(file) 
        
        ###4. 필드에러###
        data_count = 0
        data_error_count = 0
        korean_count = 0
        korean_error_count = 0
        field_error_count = 0
        with open(file, 'r', encoding='utf-8') as f:
            json_datas = json.load(f)
        # JSON 데이터 탐색 시작
        for j in range(len(json_datas)):
            data_count += 1
            json_data = json_datas[j]
            size = len(json_datas)
            #print(json_data)
            field_recursive_error_counter(json_data, file) 
            data_error_count += isError #데이터 단위로 에러 파악. 1개라도 틀리면 카운팅
            isError = False
            #print(f"[{i+1}/{len(files)}] {j}/{len(json_datas)} - {file}")
            j += 1
            if (j+1) % 1000 == 0:
                sec = time.time()-start # 종료 - 시작 (걸린 시간)
                sec2 = time.time() - total_start
                times = str(datetime.timedelta(seconds = sec)) # 걸린시간 보기좋게 바꾸기
                times2 = str(datetime.timedelta(seconds = sec2)) # 걸린시간 보기좋게 바꾸기
                short = times.split(".")[0] # 초 단위 까지만
                short2 = times2.split(".")[0] # 초 단위 까지만
                print(f"[{i+1}/{files_size}] 4. 필드에러 - {file}  {j+1}/{size}. {short} sec. {short2} sec")
        data_list = sorted(data_dict.items(), key= lambda item:item[1], reverse=True) # valie를 기준으로 내림차순 정렬
        save_and_print(file)
        for key, value in data_list:
            save_and_print(f"{key}: {value} ({round(value/field_error_count*100, 2)}%)")
        save_and_print(f"필드 에러 수 : {field_error_count}")
        ###4. 필드에러 끝###

        ###5. 결합###
        data_count = 0
        data_error_count = 0
        korean_count = 0
        korean_error_count = 0
        corrected_data_list = [] # 수정된 데이터 저장할 리스트
        j = 0
        json_datas = json.load(open(file, 'r', encoding='utf-8'))
        size = len(json_datas)
        for json_data in json_datas[j:]:
            data_count += 1
            corrected_data = combination_recursive(json_data, file)
            data_error_count += isError #데이터 단위로 에러 파악. 1개라도 틀리면 카운팅
            isError = False
            corrected_data_list.append(corrected_data) #jon파일 만들기 위해서 리스트에 저장. 파일저장안하면 코드 주석
            j += 1
            if (j+1) % 1000 == 0:
                sec = time.time()-start # 종료 - 시작 (걸린 시간)
                sec2 = time.time() - total_start
                times = str(datetime.timedelta(seconds = sec)) # 걸린시간 보기좋게 바꾸기
                times2 = str(datetime.timedelta(seconds = sec2)) # 걸린시간 보기좋게 바꾸기
                short = times.split(".")[0] # 초 단위 까지만
                short2 = times2.split(".")[0] # 초 단위 까지만
                print(f"[{i+1}/{files_size}] 5. 결합 - {file}  {j+1}/{size}. {short} sec. {short2} sec")
        ###5. 결합 끝###


        ###6. json 파일 생성### 
        output_file = file.replace('.json', '_corrected.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(corrected_data_list, f, ensure_ascii=False, indent=4)
        print(f"파일 '{file}'의 오타를 수정하고 '{output_file}'로 저장했습니다.")
        ###6. json 파일 생성 끝### 
        
        sec = time.time()-start # 종료 - 시작 (걸린 시간)
        times = str(datetime.timedelta(seconds=sec)) # 걸린시간 보기좋게 바꾸기
        short = times.split(".")[0] # 초 단위 까지만
        save_and_print(f"{file}")
        save_and_print(f"데이터 개수 : {data_count}")
        save_and_print(f"데이터 수정 개수 : {data_error_count}")
        save_and_print(f"데이터 에러율 : {round(data_error_count/data_count*100, 2)}%")
        save_and_print(f"")
        save_and_print(f"한글 문자열 개수 : {korean_count}")
        save_and_print(f"한글 문자열 수정 개수 : {korean_error_count}")
        save_and_print(f"한글 문자열 에러율 : {round(korean_error_count/korean_count*100, 2)}%")
        save_and_print(f"네이버 맞춤법 검사 문자열 수 : {naver_count}")
        save_and_print(f"수행시간 : {short} sec")
        save_and_print("="*20)

        total_data_count += data_count
        total_data_error_count += data_error_count
        total_korean_count += korean_count
        total_korean_error_count += korean_error_count
        total_naver_count += naver_count
        sec = time.time()-start # 종료 - 시작 (걸린 시간)
        total_time += sec 
        data_dict = {} # 필드 에러 딕셔너리 초기화
        total_field_error_count += field_error_count

    ###최종 정리###
    total_field_list = sorted(total_field_dict.items(), key= lambda item:item[1], reverse=True) # valie를 기준으로 내림차순 정렬
    for key, value in total_field_list:
        save_and_print(f"{key}: {value} ({round(value/total_field_error_count*100, 2)}%)")
        
    times = str(datetime.timedelta(seconds=total_time)) # 걸린시간 보기좋게 바꾸기
    short = times.split(".")[0] # 초 단위 까지만
    save_and_print(f"전체 데이터 개수 : {total_data_count}")
    save_and_print(f"전체 데이터 수정 개수 : {total_data_error_count}")
    save_and_print(f"전체 데이터 에러율 : {round(total_data_error_count/total_data_count*100, 2)}%")
    save_and_print(f"")
    save_and_print(f"전체 한글 문자열 개수 : {total_korean_count}")
    save_and_print(f"전체 한글 문자열 수정 개수 : {total_korean_error_count}")
    save_and_print(f"전체 한글 문자열 에러율 : {round(total_korean_error_count/total_korean_count*100, 2)}%")
    save_and_print(f"전체 네이버 맞춤법 검사 문자열 수 : {total_naver_count}")
    save_and_print(f"전체 수행시간 : {short} sec")
    save_and_print(datetime.datetime.now())
