import streamlit as st
import streamlit.components.v1 as components
import pathlib

st.set_page_config(page_title="고양이 쓰다듬기 게임", page_icon="🐱", layout="centered")

html_path = pathlib.Path(__file__).parent / "game.html"
html_code = html_path.read_text(encoding="utf-8")

st.markdown("## 🐱 고양이 쓰다듬기 게임")
st.caption("고양이가 뒤를 보고 있을 때만 살짝 쓰다듬으세요. 완전히 돌아보면 게임 오버!")

components.html(html_code, height=650, scrolling=False)

with st.expander("게임 규칙 보기"):
    st.markdown(
        """
- 고양이는 평소 **뒤돌아 있는 상태**입니다. 이때 클릭하면 **점수 +1**
- 가끔 고양이가 고개를 돌립니다:
  1. **살짝 옆을 봄** (0.8초, 점점 빨라짐) — 이때 클릭해도 안전하게 점수 획득
  2. **완전히 앞을 봄** (화난 표정, 1초) — 이때 클릭하면 **게임 오버**
  3. 다시 원래 **뒤돌아 상태**로 복귀
- 살짝 옆을 보는 시간은 점수가 오를수록 점점 짧아져서 난이도가 올라갑니다.
- 최고 기록은 브라우저에 저장되어 새로고침해도 유지됩니다. (새 게임 시작 시 타이밍은 초기화)
        """
    )
