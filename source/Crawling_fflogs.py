#fflogs에 있는 에덴 영식 레이드별 팀 이름과 클리어 시간, 세부 로그의 링크를 리턴합니다.

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time as t
import numpy as np
import pandas as pd

#드라이버를 통한 크롬 오픈
driver = webdriver.Chrome(r"chromedriver.exe")


for boss in range(65, 69):
    # 층
    if boss == 65:
        floor = '1'
    elif boss == 66:
        floor = '2'
    elif boss == 67:
        floor = '3'
    else:
        floor = '4'
    ranking = 10
    html = "https://www.fflogs.com/zone/rankings/29#boss="+str(boss)

    flag = False
    #크롤링 당시 웹페이지는 최대 50 페이지 미만이었기 때문에 50으로 지정  
    for page in range(1,50):
        ranking = (page-1)*50+1
        if page > 1:
            html = "https://www.fflogs.com/zone/rankings/29#boss=" + str(boss)+"&page="+str(page)
        print(page, html)

        #트래픽 부하 방지 및 차단 방지를 위한 wait 
        driver.implicitly_wait(3)
        #웹페이지가 없는 경우
        try:
            driver.get(html)
        except StaleElementReferenceException:
            print("페이지 없음")
            break;
        resultArray = np.array([['층', '팀 이름', '유저 이름', '직업', 'DPS', 'RDPS', 'DPS 관련 링크','시간']])
        imsi = np.array([['팀 이름', '시간', '링크']])
        for idx in range(0,50):
            try:
                #팀, 시간, 세부 링크, 세부 기록을 위해 임시 저장을 하는 array, 팀 랭킹 등을 기록
                team = driver.find_element_by_css_selector(''.join(["#row-",str(boss),"-",str(ranking)," > td.main-table-name > div > div.fights-table-name > a"]))
                duration = driver.find_element_by_css_selector(''.join(["#row-",str(boss),"-", str(ranking)," > td.fights-table-duration.main-table-number.primary"]))
                link = driver.find_element_by_xpath(''.join(['//*[@id="row-', str(boss),'-', str(ranking), '"]/td[2]/div/div[1]/a'])).get_attribute('href')
                imsi = np.vstack([imsi, [team.text, duration.text, link]])
                ranking += 1
            except NoSuchElementException:
                flag = True
                break
        #이후 세부 링크를 참조하여 팀 별 레코드를 기록    
        for idx in range(1, len(imsi)):
            hhtml = imsi[idx][2]
            driver.get(hhtml)
            try:
                table = driver.find_element_by_css_selector('#main-table-0')
                tbody = table.find_element_by_tag_name('tbody')
                trs = tbody.find_elements_by_tag_name('tr')
            except NoSuchElementException:
                print("기록이 없습니다 : ", imsi[idx][0])
                continue
            for i in range(0, len(trs), 2):
                ID = trs[i].get_attribute('id')
                user = driver.find_element_by_css_selector(''.join(['#', ID,
                                                                        ' > td.main-table-name.report-table-name > table > tbody > tr > td.tooltip.main-table-link > a'])).text
                user_class = driver.find_element_by_css_selector(''.join(['#', ID,
                                                                              ' > td.main-table-name.report-table-name > table > tbody > tr > td.tooltip.main-table-link > a'])).get_attribute(
                        'class')
                dps = driver.find_element_by_css_selector(
                        ''.join(['#', ID, ' > td.main-table-number.primary.main-per-second-amount'])).text
                rdps = driver.find_element_by_css_selector(
                        ''.join(['#', ID, ' > td.main-table-number.tooltip.rdps.main-per-second-amount'])).text

                user_class = str(user_class).replace('\n', '')
                dps = str(dps).replace('"', '')
                rdps = str(rdps).replace('"', '')

                _num = str(ID).replace('main-table-row-', '')
                _num = _num.replace('-0', '')

                dps_link = hhtml+'source='+ _num
                print([floor, [imsi[idx][0], user, user_class, dps, rdps, dps_link, imsi[idx][1]]])
                resultArray = np.vstack([resultArray, [floor, imsi[idx][0], user, user_class, dps, rdps, dps_link, imsi[idx][1]]])
            t.sleep(1)
        #파일 저장 
        DF = pd.DataFrame(resultArray)
        DF.to_csv(path_or_buf=''.join([r'에덴',floor,'층\Team_Ranking_result', str(boss),'_', str(ranking-50),'.txt']),
            header=False, index=False, encoding='utf-8')

        if flag == True:
            break;
        t.sleep(3)
#드라이버 종료 
driver.quit()
