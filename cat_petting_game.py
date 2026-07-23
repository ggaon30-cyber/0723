"""
🐱 고양이 쓰다듬기 게임 (Streamlit)
------------------------------------------------
[게임 규칙]
1. 고양이는 평소 '뒤돌아 있는 상태(back)'이며, 이때 쓰다듬으면 +1점.
2. 무작위 시간(기본 1.2~3.0초)이 지나면 고양이가 슬쩍 '옆을 보는 상태(side)'로 전환된다.
   - 이 상태는 "곧 정면을 볼 것"이라는 경고 신호.
   - 지속 시간은 0.8초에서 시작해 점수가 오를수록 점점 짧아진다(난이도 상승).
3. side 상태가 끝나면 고양이가 '완전히 정면을 보는 상태(front, 살짝 화난 표정)'가 되어 1초간 유지.
   - 이때 쓰다듬으면 게임 오버!
4. front 상태가 끝나면 다시 back 상태로 돌아가 사이클이 반복된다.
5. 새 게임을 시작하면 난이도(경고 지속시간 등)는 처음 값으로 초기화된다.
6. 최고 기록은 로컬 파일에 저장되어 앱을 껐다 켜도 유지된다.

[실행 방법]
    pip install streamlit
    streamlit run cat_petting_game.py

[참고]
- "약간 옆(경고) 상태 지속시간이 시간이 지날수록 느려진다"는 원문 설명은
  일반적인 난이도 곡선상 반대(짧아짐=어려워짐)의 오타로 보여, 아래에서는
  점수가 오를수록 경고 시간이 '짧아지는' 방향으로 구현했습니다.
  반대로 점점 길어지길 원하시면 SIDE_DURATION_DECAY_PER_POINT 값을
  음수로 바꾸면 됩니다.
"""

import streamlit as st
import time
import random
import json

# =========================================================
# 게임 밸런스 상수 (필요하면 자유롭게 조정하세요)
# =========================================================
BACK_MIN_INTERVAL = 1.2                 # back 상태 최소 유지 시간(초)
BACK_MAX_INTERVAL = 3.0                 # back 상태 최대 유지 시간(초)
SIDE_DURATION_START = 0.8               # side(경고) 상태 시작 지속시간(초)
SIDE_DURATION_MIN = 0.3                 # side 상태 최소 지속시간(난이도 상한)
SIDE_DURATION_DECAY_PER_POINT = 0.015   # 점수 1점당 side 지속시간 감소량
FRONT_DURATION = 1.0                    # front(위험) 상태 지속 시간(초)
TICK = 0.08                             # 화면 갱신 주기(초) - 애니메이션 부드러움 조절

HIGH_SCORE_FILE = "cat_game_high_score.json"

STATUS_INFO = {
    "back":  {"emoji": "🐈", "badge": "🟢", "msg": "지금은 안전해요! 마음껏 쓰다듬으세요"},
    "side":  {"emoji": "😼", "badge": "🟡", "msg": "어라...? 고개를 돌리고 있어요. 조심하세요!"},
    "front": {"emoji": "😾", "badge": "🔴", "msg": "위험! 지금 만지면 게임 오버예요!"},
}

# =========================================================
# 최고 기록 파일 입출력 (앱을 다시 실행해도 기록 유지)
# =========================================================
def load_high_score() -> int:
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as f:
            return int(json.load(f).get("high_score", 0))
    except Exception:
        return 0


def save_high_score(score: int) -> None:
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": score}, f)
    except Exception:
        pass  # 파일 저장이 불가능한 환경이어도 게임 진행에는 문제 없음


# =========================================================
# 세션 상태 초기화
# =========================================================
def start_new_game():
    st.session_state.game_started = True
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.cat_state = "back"
    st.session_state.state_start = time.time()
    st.session_state.next_interval = random.uniform(BACK_MIN_INTERVAL, BACK_MAX_INTERVAL)
    st.session_state.new_high_score = False


if "high_score" not in st.session_state:
    st.session_state.high_score = load_high_score()

if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.cat_state = "back"
    st.session_state.state_start = time.time()
    st.session_state.next_interval = random.uniform(BACK_MIN_INTERVAL, BACK_MAX_INTERVAL)
    st.session_state.new_high_score = False


# =========================================================
# 게임 로직
# =========================================================
def current_side_duration(score: int) -> float:
    """점수가 오를수록 짧아지는 경고(side) 지속시간 (최소값으로 하한 고정)"""
    duration = SIDE_DURATION_START - score * SIDE_DURATION_DECAY_PER_POINT
    return max(duration, SIDE_DURATION_MIN)


def update_cat_state():
    """시간 경과에 따라 고양이 상태를 back -> side -> front -> back 순으로 전환"""
    if not st.session_state.game_started or st.session_state.game_over:
        return

    elapsed = time.time() - st.session_state.state_start
    state = st.session_state.cat_state

    if state == "back" and elapsed >= st.session_state.next_interval:
        st.session_state.cat_state = "side"
        st.session_state.state_start = time.time()

    elif state == "side" and elapsed >= current_side_duration(st.session_state.score):
        st.session_state.cat_state = "front"
        st.session_state.state_start = time.time()

    elif state == "front" and elapsed >= FRONT_DURATION:
        st.session_state.cat_state = "back"
        st.session_state.state_start = time.time()
        st.session_state.next_interval = random.uniform(BACK_MIN_INTERVAL, BACK_MAX_INTERVAL)


def touch_cat():
    """플레이어가 고양이를 터치했을 때 처리"""
    if st.session_state.cat_state == "front":
        st.session_state.game_over = True
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
            st.session_state.new_high_score = True
            save_high_score(st.session_state.score)
    else:
        st.session_state.score += 1


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(page_title="고양이 쓰다듬기 게임", page_icon="🐱", layout="centered")
st.title("🐱 고양이 쓰다듬기 게임")

# =========================================================
# 화면 1) 시작 전
# =========================================================
if not st.session_state.game_started:
    st.write("고양이가 뒤돌아 있을 때만 몰래 쓰다듬어보세요. 정면을 보면 절대 만지면 안 돼요!")

    with st.expander("📖 게임 방법", expanded=True):
        st.markdown(
            """
            - 🟢 **뒤돌아 있을 때**: 안심하고 쓰다듬으면 **+1점**
            - 🟡 **슬쩍 옆을 볼 때**: 곧 정면을 볼 거라는 경고예요. 신중하게 판단하세요.
            - 🔴 **완전히 정면을 볼 때**: 이때 만지면 **게임 오버**!
            - 점수가 오를수록 경고(옆모습) 시간이 점점 짧아져서 더 어려워져요.
            """
        )

    if st.session_state.high_score > 0:
        st.info(f"🏆 현재 최고 기록: **{st.session_state.high_score}점**")

    if st.button("게임 시작하기 🎮", key="start_btn", use_container_width=True):
        start_new_game()
        st.rerun()

# =========================================================
# 화면 2) 게임 오버
# =========================================================
elif st.session_state.game_over:
    st.markdown("## 😾 GAME OVER!")

    if st.session_state.new_high_score:
        st.success(f"🎉 신기록입니다! {st.session_state.score}점")
        st.balloons()
    else:
        st.error(f"이번 점수: {st.session_state.score}점")

    st.info(f"🏆 최고 기록: {st.session_state.high_score}점")

    if st.button("다시 시작하기 🔁", key="restart_btn", use_container_width=True):
        start_new_game()
        st.rerun()

# =========================================================
# 화면 3) 게임 플레이 중
# =========================================================
else:
    update_cat_state()

    col1, col2 = st.columns(2)
    col1.metric("현재 점수", st.session_state.score)
    col2.metric("최고 기록", st.session_state.high_score)

    info = STATUS_INFO[st.session_state.cat_state]
    st.markdown(f"### {info['badge']} {info['msg']}")
    st.caption(f"현재 경고(옆모습) 지속시간: {current_side_duration(st.session_state.score):.2f}초")

    # 고양이 버튼만 크게 보이도록 이 화면에서만 스타일 적용
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] button {
            font-size: 110px !important;
            line-height: 1 !important;
            height: 230px;
            width: 100%;
            border-radius: 24px;
            border: 3px solid #e0c9a6;
            background: linear-gradient(180deg, #fff7ec 0%, #ffe9c7 100%);
            transition: transform 0.08s ease-in-out;
        }
        div[data-testid="stButton"] button:active {
            transform: scale(0.96);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    clicked = st.button(info["emoji"], key="cat_button", use_container_width=True)

    if clicked:
        touch_cat()
        st.rerun()

    # 사용자의 클릭이 없어도 시간 경과에 따라 상태가 자동 전환되도록
    # 짧은 주기로 화면을 계속 갱신한다.
    time.sleep(TICK)
    st.rerun()
