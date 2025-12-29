from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # 세션을 사용하기 위한 비밀키 설정

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

@app.route('/')
def home():
    session.clear()
    return redirect(url_for('questions1_4'))

@app.route('/questions1_4', methods=['GET', 'POST'])
def questions1_4():
    if request.method == 'POST':
        session['question1'] = request.form.getlist('environment')
        session['question2'] = request.form.getlist('genre')
        session['question3'] = request.form.getlist('instrument')
        session['question4'] = [request.form.get('focus')]  # 단일 선택
        return redirect(url_for('questions5_8'))
    return render_template('questions1_4.html')

@app.route('/questions5_8', methods=['GET', 'POST'])
def questions5_8():
    if request.method == 'POST':
        session['question5'] = [request.form.get('emotion')]  # 단일 선택
        session['question6'] = request.form.getlist('activity')
        session['question7'] = [request.form.get('genre_preference')]  # 단일 선택
        session['question8'] = request.form.getlist('discovery')
        return redirect(url_for('result'))
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
        explanations.append("당신은 클럽이나 사람 많은 장소에서 음악 듣는 것을 좋아하는 경향이 있네요.")
        explanations.append("신나는 음악과 활동적인 분위기를 선호하는 것 같습니다.")
    else:
        explanations.append("당신은 혼자 조용한 곳에서 음악을 듣는 것을 좋아하는 경향이 있네요.")
        explanations.append("차분하고 감성적인 음악을 즐기는 것 같습니다.")

    # N/S 설명
    if scores['N'] > scores['S']:
        explanations.append("직관적인 사람으로서 음악의 깊은 의미와 상징성에 끌리는 경향이 있습니다.")
    else: 
        explanations.append("감각적인 사람으로서 구체적이고 즉각적으로 느껴지는 멜로디나 리듬을 중요하게 여깁니다.")

    # T/F 설명
    if scores['T'] > scores['F']:
        explanations.append("현실적인 노래를 선호하며, 음악을 통해 생각하고 분석하는 경향이 있습니다.")
    else:
        explanations.append("감정적인 사람으로서 음악을 통해 감정을 표현하고 느끼는 것을 좋아합니다.")

    # J/P 설명
    if scores['J'] > scores['P']:
        explanations.append("계획적인 성향을 가지고 있으며, 체계적으로 음악을 탐색하는 것을 좋아합니다.")
    else:
        explanations.append("즉흥적이고 자유로운 성향으로, 새로운 음악을 즉각적으로 발견하고 즐깁니다.")

    # 결과 페이지에 선택 항목과 MBTI 유형 및 설명 전달
    return render_template(
        'result.html', 
        mbti_type=mbti_type,
        selections=selections,
        explanations=explanations
    )

if __name__ == '__main__':
    app.run(debug=True)
