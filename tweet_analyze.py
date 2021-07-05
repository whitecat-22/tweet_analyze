import pandas as pd
import streamlit as st


def main():
    """
    mainの実行部分
    """
    df_users = pd.read_csv('./result_userdata/users.csv')
    # サイドバーにselectboxの表示
    add_selectbox = st.sidebar.selectbox(
        "データを見たいユーザーを選択",
        df_users.iloc[0]
        )

    screenname = add_selectbox

    # フォロワー数のデータフレームのローカルからの読み込み
    df_base = pd.read_csv(f'./result_userdata/{screenname}_info.csv')

    df_base['Date'] = pd.to_datetime(df_base['Date'])
    df_base.set_index('Date', inplace=True)

    # ツイートデータの読み込み
    df_tweet_data = pd.read_csv(f'./result_userdata/{screenname}_tweet_data.csv')

    df_tweet_data['つぶやき日時'] = pd.to_datetime(df_tweet_data['つぶやき日時'])
    df_buzz = df_tweet_data.set_index('つぶやき日時')

    # streamlitの記述
    st.title('Twitter Analysis')
    st.subheader(df_tweet_data.iloc[0, 0])
    st.subheader(f'@{screenname}')
    st.subheader('フォロワー推移グラフ')

    st.line_chart(df_base['followers'])
    st.write(df_base['followers'])

    st.subheader('フォロワー日時増減')
    if df_base.shape[0] >= 2:
        st.bar_chart(df_base.diff().iloc[1:])
    else:
        st.write('データが不足しています。')

    st.subheader('Top Tweets')
    st.line_chart(df_buzz.loc[:, ['いいね数', 'RT数']])
    st.subheader('ツイートデータ(いいね+RT数>30)')
    st.dataframe(df_tweet_data.loc[:, [
                'いいね数', 'RT数', 'つぶやき日時', '本文']].style.highlight_max(axis=0))


if __name__ == '__main__':
    main()
