from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import librosa
import csv
import os
import random
from librosa.sequence import dtw
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 세션을 사용하기 위한 비밀키 설정
# 음악 파일이 있는 디렉토리 경로와 CSV 파일 경로 설정
music_dir = "C:/Users/kjp60/.spyder-py3/static/"
output_csv_path = os.path.join(music_dir, "music_mfcc_features.csv")
# 장르 라벨링
genre_labels = {
    "Rap": 1,
    "Roc": 2,
    "Bal": 3,
    "Jazz": 4,
    "Kpop": 5,
    "Trt": 6,
    "Cla": 7,
    "Pop": 8
}
# 질문별 점수
score_mapping = {
    'question1': {
        'club': {'E': 10},
        'concert': {'E': 7},
        'home': {'I': 8},
        'walking': {'I': 6},
        'work': {'I': 6},
    },
    'question2': {
        'rock': {'E': 5},
        'ballad': {'I': 5},
        'trot': {'E': 4},
        'jazz': {'I': 5},
        'rap': {'E': 4, 'T': 2},
- 23 
        'kpop': {'E': 4},
        'pop': {'I': 3, 'E': 2},
        'classical': {'I': 4, 'F': 2},
    },
    'question3': {
        'bass': {'I': 4, 'E': 3},
        'piano': {'I': 4},
        'strings': {'I': 4},
        'acoustic_guitar': {'I': 4},
        'drum': {'E': 5},
        'electric_guitar': {'E': 5},
        'woodwind': {'I': 3},
        'synthesizer': {'I': 3, 'E': 3},
    },
    'question4': {
        'lyrics': {'N': 10, 'T': 4},
        'melody': {'S': 10, 'F': 5},
    },
    'question5': {
        'emotional': {'F': 5},
        'energetic': {'T': 5},
    },
    'question6': {
        'search_new': {'P': 5},
        'make_playlist': {'J': 5},
        'attend_concert': {'J': 6},
        'find_random': {'P': 6},
    },
    'question7': {
        'explore_new': {'N': 5},
        'stick_genre': {'S': 5},
    },
    'question8': {
        'self_search': {'P': 5},
        'random_discovery': {'P': 5},
        'short_form': {'P': 4},
        'recommend_list': {'J': 5},
        'other_recommendation': {'J': 5},
    }
}
# MBTI 유형에 따른 추천 장르 매핑
mbti_genre_mapping = {
    'ISTJ': 'Cla',  # 클래식
    'ISFJ': 'Bal',  # 발라드
- 24 
    'INFJ': 'Jazz',  # 재즈
    'INTJ': 'Roc',  # 락
    'ISTP': 'Roc',  # 락
    'ISFP': 'Kpop',  # K-pop
    'INFP': 'Pop',  # 팝
    'INTP': 'Jazz',  # 재즈
    'ESTP': 'Rap',  # 랩
    'ESFP': 'Kpop',  # K-pop
    'ENFP': 'Pop',  # 팝
    'ENTP': 'Jazz',  # 재즈
    'ESTJ': 'Trt',  # 트로트
    'ESFJ': 'Bal',  # 발라드
    'ENFJ': 'Bal',  # 발라드
    'ENTJ': 'Rap',  # 랩
}
# 각 MBTI 유형에 대한 설명 매핑
mbti_descriptions = {
    'ISTJ': '현실적이고 신뢰할 수 있는 관리자형',
    'ISFJ': '헌신적이고 배려 깊은 수호자형',
    'INFJ': '이상적인 사람들을 돕는 예언자형',
    'INTJ': '전략적인 사고와 계획을 중시하는 전략가형',
    'ISTP': '냉철하고 실용적인 장인형',
    'ISFP': '따뜻하고 감각적인 예술가형',
    'INFP': '이상주의적이고 창의적인 중재자형',
    'INTP': '논리적이고 분석적인 사색가형',
    'ESTP': '활동적이고 현실적인 사업가형',
    'ESFP': '사교적이고 쾌활한 연예인형',
    'ENFP': '열정적이고 상상력이 풍부한 활동가형',
    'ENTP': '논쟁적이고 독창적인 발명가형',
    'ESTJ': '현실적이고 리더십이 강한 관리자형',
    'ESFJ': '배려 깊고 사교적인 제공자형',
    'ENFJ': '열정적이고 사람을 이끄는 선도자형',
    'ENTJ': '열정적이고 목표 지향적인 통솔자형',
}
# 곡 경로와 정보를 읽어오는 함수
def read_song_data(csv_file):
    song_data = []
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 건너뛰기
        for row in reader:
            song_path = row[0]
            genre = row[1]
- 25 
            song_name = row[2]
            mfcc_values = list(map(float, row[3:]))  # MFCC 값은 4번째 열부터 시작
            song_data.append((song_path, genre, song_name, mfcc_values))
    return song_data
# 점수를 계산하는 함수
def calculate_scores(user_features, genre_features):
    D, wp = dtw(np.array(user_features).reshape(-1, 1), 
np.array(genre_features).reshape(-1, 1))
    dtw_distance = np.sum(D[wp[:, 0], wp[:, 1]])
    
    # MFCC 중요도 설정
    importance_weights = [0.8] * 2 + [0.4] * 5 + [0.2] * 6
    weighted_distance = dtw_distance * np.mean(importance_weights)
    max_possible_distance = np.sqrt(sum([100**2 * w for w in importance_weights]))
    score = max(0, 100 - (weighted_distance / max_possible_distance) * 100)
    
    return score
# 점수 계산 함수
def calculate_mbti_score(selections):
    scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    for question, choices in selections.items():
        for choice in choices:
            for trait, points in score_mapping[question].get(choice, {}).items():
                scores[trait] += points
    
    return scores
# MBTI 결과 예측 함수
def predict_mbti(scores):
    mbti = ''
    mbti += 'E' if scores['E'] > scores['I'] else 'I'
    mbti += 'S' if scores['S'] > scores['N'] else 'N'
    mbti += 'T' if scores['T'] > scores['F'] else 'F'
    mbti += 'J' if scores['J'] > scores['P'] else 'P'
    return mbti
# 추천 곡을 찾는 함수
def recommend_songs(user_features, input_song_name, selected_song, mbti_type):
    song_data = read_song_data(output_csv_path)
    all_scores = []
    genre_best_song = {genre: [] for genre in genre_labels.keys()}
- 26 
    # 입력 곡의 장르 찾기
    input_genre = None
    for song_path, genre, song_name, mfcc_values in song_data:
        print(f"현재 곡명: {song_name}  입력곡: {input_song_name}")
        if song_name == input_song_name:             
            input_genre = genre
            break
    for song_path, genre, song_name, mfcc_values in song_data:
        score = calculate_scores(user_features, mfcc_values)
        # 100점인 곡은 제외
        if score < 99:
            all_scores.append((song_path, genre, song_name, score))
            genre_best_song[genre].append((song_name, score))
    # 장르별 평균 점수 계산
    average_scores = {}
    for genre in genre_labels.keys():
        genre_scores = [score for _, g, song_name, score in all_scores if g == genre]
        if genre_scores:
            average_scores[genre] = np.mean(genre_scores)
            if genre == input_genre:
                average_scores[genre] += 12
                
    recommended_songs = []
    sorted_average_scores = sorted(average_scores.items(), key=lambda x: x[1], 
reverse=True)
    # 상위 3곡 선정
    if sorted_average_scores:
        highest_avg_genre = sorted_average_scores[0][0]
        top_song = max(genre_best_song[highest_avg_genre], key=lambda x: x[1])  
        recommended_songs.append((top_song[0], top_song[1], highest_avg_genre))
        if len(genre_best_song[highest_avg_genre]) > 1:
            second_best_song = sorted(genre_best_song[highest_avg_genre], key=lambda x: 
x[1], reverse=True)[1]
            recommended_songs.append((second_best_song[0], second_best_song[1], 
highest_avg_genre))
        if len(sorted_average_scores) > 1:
            second_highest_avg_genre = sorted_average_scores[1][0]
            top_second_genre_song = max(genre_best_song[second_highest_avg_genre], 
key=lambda x: x[1])
- 27 
            recommended_songs.append((top_second_genre_song[0], top_second_genre_song[1], 
second_highest_avg_genre))
    # MBTI 유형에 따른 장르 추가 (4번째 추천)
    mbti_genre = mbti_genre_mapping.get(mbti_type, None)  # MBTI에 해당하는 장르 얻기
    if mbti_genre:
        # MBTI 장르에 해당하는 곡을 찾기
        mbti_songs = [song for song in song_data if song[1] == mbti_genre]
        if mbti_songs:
            random_mbti_song = random.choice(mbti_songs)
            recommended_songs.append((random_mbti_song[2], 0, random_mbti_song[1]))  # 점
수는 0으로 설정
    # 점수가 99.9 이상인 곡을 추천 목록에서 제외하고 중복 제거
    unique_recommended_songs = []
    for song in recommended_songs:
        score = song[1]  # 곡의 점수
        if score < 99.9:  # 점수가 99.9 미만인 경우만 추가
            if song[0] not in [s[0] for s in unique_recommended_songs]:  # 곡명이 중복되
지 않도록 확인
                unique_recommended_songs.append(song)
    print("최종 추천 곡:", unique_recommended_songs)  # 추천 곡 출력
    return unique_recommended_songs[:4], average_scores  # 4곡 추천
@app.route('/')
def home():
    session.clear()  # 세션 초기화
    return render_template('home.html')
@app.route('/index', methods=['GET', 'POST'])
def question1():
    if request.method == 'POST':
        selected_song = request.form['selected_song']
        session['selected_song'] = selected_song  # 선택한 곡을 세션에 저장
        return redirect(url_for('questions1_4'))  # questions1_4로 리디렉션
    song_data = read_song_data(output_csv_path)
    song_paths = [data[0] for data in song_data]
    return render_template('index.html', song_paths=song_paths)
@app.route('/questions1_4', methods=['GET', 'POST'])
- 28 
def questions1_4():
    if request.method == 'POST':
        session['question1'] = request.form.getlist('environment')
        session['question2'] = request.form.getlist('genre')
        print("선택한 장르:", session['question2'])  # 디버그 출력
        session['question3'] = request.form.getlist('instrument')
        session['question4'] = [request.form.get('focus')]
        return redirect(url_for('questions5_8'))
    return render_template('questions1_4.html')
@app.route('/questions5_8', methods=['GET', 'POST'])
def questions5_8():
    if request.method == 'POST':
        session['question5'] = [request.form.get('emotion')]  # 단일 선택
        session['question6'] = request.form.getlist('activity')  # 다중 선택
        session['question7'] = [request.form.get('genre_preference')]  # 단일 선택
        session['question8'] = request.form.getlist('discovery')  # 다중 선택
        return redirect(url_for('result'))  # 결과 페이지로 리디렉션
    return render_template('questions5_8.html')
@app.route('/result')
def result():
    # 사용자가 선택한 항목 가져오기
    selections = {f'question{i+1}': session.get(f'question{i+1}', []) for i in range(8)}
    
    # 점수 계산 및 MBTI 예측
    scores = calculate_mbti_score(selections)
    mbti_type = predict_mbti(scores)
    # 각 성향에 따른 설명 추가
    explanations = []
    # E/I 설명
    if scores['E'] > scores['I']:
        explanations.append("당신은 활동적이고 사람이 많은 장소에서 음악을 듣는 것을 좋아
하는 성격이군요!")
        explanations.append("신나는 음악과 활동적인 분위기를 선호하는 것 같습니다.")
    else:
        explanations.append("당신은 혼자 조용한 곳에서 음악을 듣는 것을 좋아하는 성격이군
요!")
        explanations.append("차분하고 감성적인 음악을 즐기는 것 같습니다.")
    # N/S 설명
- 29 
    if scores['N'] > scores['S']:
        explanations.append("또한 직관적인 사람으로서 음악의 깊은 의미와 상징성에 끌리는 
경향이 있으며")
    else: 
        explanations.append("또한 감각적인 사람으로서 즉각적으로 느껴지는 멜로디나 리듬에 
끌리는 경향이 있으며")
    # T/F 설명
    if scores['T'] > scores['F']:
        explanations.append("현실적인 노래를 선호하며, 음악을 통해 생각하고 분석하는 경향
이 있습니다.")
    else:
        explanations.append("감정적인 사람으로서 음악을 통해 감정을 표현하고 느끼는 것을 
좋아합니다.")
    # J/P 설명
    if scores['J'] > scores['P']:
        explanations.append("계획적인 성향을 가지고 있으며, 체계적으로 음악을 탐색하는 것
을 즐기는 당신!")
    else:
        explanations.append("즉흥적이고 자유로운 성향으로, 새로운 음악을 찾는 것을 즐기는 
당신!")
    # MBTI 유형에 따른 설명 추가
    mbti_description = mbti_descriptions.get(mbti_type, "알 수 없는 유형입니다.")
    
    # 결과 페이지에 선택 항목과 MBTI 유형 및 설명 전달
    return render_template(
        'result.html', 
        mbti_type=mbti_type,
        mbti_description=mbti_description,  # 추가된 부분
        selections=selections,
        explanations=explanations
    )
@app.route('/process', methods=['POST'])
def process():
    if request.method != 'POST':
        return redirect(url_for('home'))  # POST가 아닐 경우 홈으로 리디렉션
    selected_song = request.form['song']  # 선택한 곡의 경로 가져오기
    
    # static 디렉토리에서 파일 경로 설정
    full_song_path = os.path.join(music_dir, selected_song).replace('\\', '/')  # 전체 경
- 30 
로 생성
    # 선택한 곡의 MFCC 계산
    y, sr = librosa.load(full_song_path, offset=15.0, duration=30.0)  # full_song_path 사
용
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    user_features = [np.mean(mfcc[i]) for i in range(13)]
    
    # 선택한 곡 제목 추출
    # 선택한 곡 제목 추출
    file_name = os.path.basename(full_song_path)  # 파일 이름 추출
    parts = file_name[:-4].split('_')  # 확장자 제거 후 언더스코어로 분리
    if len(parts) >= 2:
        input_song_name = '_'.join(parts[1:])  # 마지막 부분을 제외하고 나머지를 결합
    else:
        input_song_name = file_name  # 기본적으로 파일 이름
    # MBTI 유형 가져오기
    selections = {f'question{i+1}': session.get(f'question{i+1}', []) for i in range(8)}
    scores = calculate_mbti_score(selections)
    mbti_type = predict_mbti(scores)
    # 추천 시스템을 통해 추천 곡 가져오기
    recommended_songs, average_scores = recommend_songs(user_features, input_song_name, 
full_song_path, mbti_type)  # mbti_type 전달
    # 선택한 곡의 이름만 반환
    selected_song_name = file_name  # 곡명만 사용
    # unique_recommended_songs를 사용하여 추천 목록을 반환
    return render_template('recommendations.html', selected_song=selected_song_name, 
recommendations=recommended_songs, average_scores=average_scores)
if __name__ == '__main__':
    app.run(debug=False)
