import streamlit as st
import pandas as pd
import re

def clean_data(df):
    df=df.drop_duplicates().reset_index(drop=True)

    if "Google地圖連結" in df.columns:
        canonical_name_map=(
            df.groupby("Google地圖連結")["景點名稱"]
            .agg(lambda x:x.value_counts().idxmax())
        )
        df["景點名稱"]=df["Google地圖連結"].map(canonical_name_map)
    return df

st.set_page_config(
    page_title="📍旅遊資料統整小管家",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* 卡片本體：拿掉底部圓角、按鈕接在下面 */
.spot-card {
    background-color: white;
    padding: 24px 24px 16px 24px;
    border-radius: 16px 16px 0 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border: 1px solid #f0f0f0;
    border-bottom: none;
}

/* 鎖定卡片底下緊接著的按鈕，把它改造成「無縫銜接的那排字」 */
div[data-testid="stButton"] button {
    width: 100%;
    background-color: white;
    border: 1px solid #f0f0f0;
    border-top: 1px solid #f0f0f0;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    color: #95a5a6;
    font-size: 14px;
    text-align: left !important;
    padding: 10px 24px 14px 24px;
    margin-top: -1px;
    display: flex !impotant;
    justify-content: flex-start !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #f8fafc;
    color: #0087b4;
    border-color: #f0f0f0;
}

div[data-testid="stButton"] button p {
    text-align: left !imporatnt;
    width:100%;
}
/* ---------- 手機響應式優化 ---------- */

/* 整體頁面左右留白在小螢幕縮小，避免內容被邊界擠壓 */
.block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 卡片標題：用 clamp 讓字級依螢幕寬度自動縮放，最小18px、最大24px */
.spot-card h2 {
    font-size: clamp(18px, 5vw, 24px) !important;
}

/* 詳細頁主標題：最小22px、最大32px */
.detail-title {
    font-size: clamp(22px, 6vw, 32px) !important;
}

/* 標題列（名稱 + 推薦數標籤）窄螢幕時自動換行，不擠壓 */
.title-row {
    flex-wrap: wrap;
    gap: 8px;
}

/* hashtag 標籤窄螢幕時自動換行 */
.hashtag-row {
    flex-wrap: wrap;
    row-gap: 8px;
}

/* 旅人筆記卡片：窄螢幕時改成上下排列，避免作者膠囊跟文字擠在一行 */
@media (max-width: 480px) {
    .note-card {
        flex-wrap: wrap;
    }
    .note-card .note-text {
        flex-basis: 100%;
        margin-top: 8px;
    }
}
</style>
""", unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page="list"
if "spot" not in st.session_state:
    st.session_state.spot=""

def go_to_detail(spot_name):
    st.session_state.page="detail"
    st.session_state.spot=spot_name

def go_to_list():
    st.session_state.page="list"
    st.session_state.spot=""

current_page = st.session_state.page
target_spot=st.session_state.spot

if current_page=="detail":
    st.button("← 返回首頁列表",on_click=go_to_list)
    st.write("")

if current_page=="list":
    st.markdown(
    '<h1 style="font-size: clamp(22px, 6vw, 36px); margin-bottom: 0;">✨ 旅人時光 ‧ 專屬旅遊小管家</h1>',
    unsafe_allow_html=True
    )
    st.markdown("##### 立刻為您製作專屬旅遊懶人包！")


    if "saved_df" not in st.session_state:
        
        uploaded_file=st.file_uploader(
        "請上傳您的CSV檔案",
        type=["csv"],
        help="上傳CSV檔後，下方會浮現您的專屬景點卡。"
        )

        if uploaded_file is not None:
            raw_df=pd.read_csv(uploaded_file,header=1,encoding="utf-8-sig")
            st.session_state.saved_df=clean_data(raw_df)
            st.rerun()
    else:
        with st.container(border=True):
            col1,col2=st.columns([3.5,1.5])
            with col1:
                st.markdown(f"📄 **已上傳檔案** 共{len(st.session_state.saved_df)}筆旅遊資料")
            with col2:
                if st.button("重新上傳",use_container_width=True):
                    del st.session_state.saved_df
                    st.rerun()
    st.write("---")

if "saved_df" in st.session_state:
    df=st.session_state.saved_df

    if current_page=="list":

        if "selected_area" not in st.session_state:st.session_state.selected_area="全部"
        if "selected_category" not in st.session_state:st.session_state.selected_category="全部"
        if "selected_theme" not in st.session_state:st.session_state.selected_theme="全部"

        #區域選單篩選

        df_for_area=df.copy()
        if st.session_state.selected_category !="全部":
            df_for_area=df_for_area[df_for_area["主要分類"]==st.session_state.selected_category]

        if st.session_state.selected_theme !="全部":
            df_for_area=df_for_area[df_for_area["主題推薦"]==st.session_state.selected_theme]

        area_option=["全部"]+list(df_for_area["區域"].unique()) 

        #主要分類選單篩選

        df_for_cat=df.copy()
        if st.session_state.selected_area !="全部":
            df_for_cat=df_for_cat[df_for_cat["區域"]==st.session_state.selected_area]

        if st.session_state.selected_theme !="全部":
            df_for_cat=df_for_cat[df_for_cat["主題推薦"]==st.session_state.selected_theme]

        category_option=["全部"]+list(df_for_cat["主要分類"].unique()) 

        #主題選單篩選

        df_for_theme=df.copy()
        if st.session_state.selected_category !="全部":
            df_for_theme=df_for_theme[df_for_theme["主要分類"]==st.session_state.selected_category]

        if st.session_state.selected_area !="全部":
            df_for_theme=df_for_theme[df_for_theme["區域"]==st.session_state.selected_area]

        theme_option=["全部"]+list(df_for_theme["主題推薦"].unique()) 

        st.write('#### 請選擇想看的類別')
        st.selectbox("選擇區域",area_option,key="selected_area")
        st.selectbox("選擇主要分類（美食/景點/購物）",category_option,key="selected_category")
        st.selectbox("選擇主題推薦",theme_option,key="selected_theme")

        #未篩選前全部顯示

        df_final=df.copy()

        if st.session_state.selected_area !="全部":
            df_final=df_final[df_final["區域"]==st.session_state.selected_area]
        
        if st.session_state.selected_category !="全部":
            df_final=df_final[df_final["主要分類"]==st.session_state.selected_category]
        
        if st.session_state.selected_theme !="全部":
            df_final=df_final[df_final["主題推薦"]==st.session_state.selected_theme]
        
        st.write(f"🔍 依據篩選條件，共顯示{df_final['景點名稱'].nunique()}個景點")

        #首頁，篩選不重複的景點
        unique_spot=df_final["景點名稱"].unique()

        for spot_name in unique_spot:
            spot_df=df_final[df_final["景點名稱"]==spot_name]
            recommend_count=len(spot_df)

            area_name=spot_df["區域"].iloc[0]
            transport=spot_df["🚇 交通"].iloc[0] if"🚇 交通" in spot_df.columns else "暫無交通資訊"
            category_name = spot_df['主要分類'].iloc[0] if '主要分類' in spot_df.columns else "未分類"

            card_html = (
                f'<div class="spot-card">'
                f'<div class="title-row" style="display: flex; justify-content: space-between; align-items: center;">'
                f'<h2 style="margin: 0; color: #2c3e50;">{spot_name}</h2>'
                f'<span style="background-color: #fff0eb; color: #ff6b4a; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold;">🔥 {recommend_count} 篇推薦</span>'
                f'</div>'
                f'<p style="color: #7f8c8d; margin: 10px 0; font-size: 15px;">📍 {area_name} &nbsp;•&nbsp; 🚇 {transport}</p>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            st.button(
                f"分類：{category_name} ｜ 點擊查看完整筆記 →",
                key=f"go_{spot_name}",
                on_click=go_to_detail,
                args=(spot_name,),
                use_container_width=True
            )
            st.write("")
    else:
        spot_detail_df=df[df["景點名稱"]==target_spot]

        if not spot_detail_df.empty:
            area_name=spot_detail_df['區域'].iloc[0]
            transport=spot_detail_df['🚇 交通'].iloc[0] if "🚇 交通" in spot_detail_df.columns else "暫無交通資訊"
            recommend_count=len(spot_detail_df)

            maps_url=spot_detail_df['Google地圖連結'].iloc[0] if "Google地圖連結" in spot_detail_df.columns else "#"

            detail_card_html=(
                f'<div style="background-color: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; margin-bottom: 24px;">'
                f'<div class="title-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">'
                f'<h1 class="detail-title" style="margin: 0; color: #2c3e50;">{target_spot}</h1>'
                f'<span style="background-color: #fff0eb; color: #ff6b4a; padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: bold;">🔥 {recommend_count} 篇推薦</span>'
                f'</div>'

                f'<div style="background-color: #f8fafc; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px;">'
                f'<p style="margin: 0 0 8px 0; color: #475569; font-size: 16px;">📍 <strong>所在區域：</strong> {area_name}</p>'
                f'<p style="margin: 0; color: #475569; font-size: 16px;">🚇 <strong>交通方式：</strong> {transport}</p>'
                f'</div>'

                f'<a href="{maps_url}" target="_blank" style="display:block; background-color:#3D6449;padding:14px;text-align: center; color: white; border-radius: 12px; font-weight: bold; font-size: 16px; text-decoration: none;">'
                f'🗺️ 開啟 Google Maps 導航'
                f'</a>'
                
                f'</div>'
            )
            st.markdown(detail_card_html,unsafe_allow_html=True)

            all_keywords=[]
            if "核心關鍵字" in spot_detail_df.columns:
                for kw_str in spot_detail_df["核心關鍵字"].dropna().tolist():
                    split_kws=[k.strip() for k in str(kw_str).replace("，", ",").replace(";", ",").replace("；", ",").split(",") if k.strip()]
                    all_keywords.extend(split_kws)
            unique_keywords=list(dict.fromkeys(all_keywords))

            if unique_keywords:
                hashtag_html="".join(
                    f'<span style="color: #0087b4; font-size: 14px; font-weight: 600; margin-right: 14px;">#{kw}</span>'
                    for kw in unique_keywords   
                )
                keyword_block_html = (
                    f'<div style="margin-bottom: 24px;">'
                    f'<p style="margin: 0 0 8px 0; color: #475569; font-size: 15px; font-weight: bold;">🏷️ 重點主題標籤：</p>'
                    f'<div class="hashtag-row" style="display: flex;">{hashtag_html}</div>'
                    f'</div>'
                )
                st.markdown(keyword_block_html, unsafe_allow_html=True)

            notes_html_list=[]

            for idx,row in spot_detail_df.iterrows():
                author=row["旅人"] if "旅人" in spot_detail_df.columns else "神秘旅人"
                single_note=row["獨家亮點"] if "獨家亮點" in spot_detail_df.columns else "點擊連結查看完整精彩內容"
                url=row["原始網址"] if "原始網址" in spot_detail_df.columns else "#"
                chrome_url=(f"{url}#:~:text={target_spot}")

                note_card_html=(
                    f'<a href="{chrome_url}" target="_blank" style="text-decoration: none; color: inherit; display: block; width: 100%; box-sizing: border-box;">'
                    f'<div class="note-card" style="background-color: white; padding: 16px 20px; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02); cursor: pointer;">'
                    f'<span style="flex-shrink: 0; background-color: #fee0e0; color: #a10303; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 500; margin-right: 12px;">💬 {author}</span>'
                    f'<span class="note-text" style="flex: 1; font-size: 15px; color: #334155;">{single_note}</span>'
                    f'<span style="flex-shrink: 0; color: #94a3b8; font-size: 16px; margin-left: 12px;">→</span>'
                    f'</div>'
                    f'</a>'
                )
                notes_html_list.append(note_card_html)   

            all_note = (
                '<div style="display: flex; flex-direction: column; gap: 12px;">'
                + "".join(notes_html_list)
                + '</div>'
            )

            raw_consensus=spot_detail_df['共識重點句子'].dropna().unique().tolist() if "共識重點句子" in spot_detail_df.columns else[]
            unique_consensus=[s for s in raw_consensus if not re.search(r"（.*）",str(s))]

            if len(unique_consensus)>0:
                consensus_items="".join(
                            f'<p style="margin: 0 0 8px 0; color: #78350f; font-size: 15px; line-height: 1.6;">✓ {sentence}</p>'
                            for sentence in unique_consensus
                )
            else:
                consensus_items='<p style="margin: 0; color: #78350f; font-size: 15px; line-height: 1.6;">這個景點只有一位旅人推薦！尚待更多旅人補充！</p>'

            consensus_html=(
                f'<div style="background-color: #fffbeb; padding: 24px; border-radius: 16px; border: 1px dashed #fcd34d; margin-bottom: 24px;">'
                f'<h4 style="margin: 0 0 10px 0; color: #b45309; font-size: 18px;">💡 旅人共識重點</h4>'
                f'{consensus_items}'
                f'</div>'
            )
            st.markdown(consensus_html,unsafe_allow_html=True)

            st.write("##### 📝 旅人獨家導航")
            st.markdown(all_note,unsafe_allow_html=True)
            st.write(" ")
            st.caption("💡 貼心提示：點擊上方任何筆記，瀏覽器將會自動開啟新分頁！")
        
        else:
            st.warning("找不到該景點的相關資料")

