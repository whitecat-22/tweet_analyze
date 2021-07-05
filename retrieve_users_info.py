import os
import tweepy
import datetime as dt
import pandas as pd


def twitter_authenticate():
    """
    各種ツイッターのキーをセット
    Twitter APIインスタンスの取得
    """
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_key = os.environ.get("ACCESS_KEY")
    access_secret = os.environ.get("ACCESS_KEY_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)  # API利用制限にかかった場合、解除まで待機する
    return api


def follower_transition(api, screenname):
    """
    スクリーンネームごとの日時のフォロワー推移の取得
    """
    # ツイート取得
    user = api.get_user(screen_name=screenname)

    list_date = []
    list_followers = []

    # フォロワー数と日付を調べる
    list_date.append(dt.date.today().strftime('%Y-%m-%d'))
    list_followers.append(user.followers_count)

    if not os.path.exists(f'./result_userdata/{screenname}_info.csv'):
        # 初回。データフレームの作成
        df_start = pd.DataFrame({'Date': list_date,
                        'followers': list_followers})

        # 最初のデータフレームの保存
        df_start.to_csv(f'./result_userdata/{screenname}_info.csv', index=False)

        df_base = df_start

    else:
        # 定期。当日分のみのデータフレームの作成
        df_today = pd.DataFrame({'Date': list_date,
                        'followers': list_followers})

        # 保存するCSVの読み込み
        df_base = pd.read_csv(f'./result_userdata/{screenname}_info.csv')
        if df_base.iloc[-1][0] != dt.date.today().strftime('%Y-%m-%d'):
            # データフレームの結合
            df_base = pd.concat([df_base, df_today])
            # indexのふり直し
            df_base = df_base.reset_index(drop=True)
            # フォロワー情報をCSVに書き込み
            df_base.to_csv(f'./result_userdata/{screenname}_info.csv', index=False)

        else:
            print(f'{screenname}の本日のフォロワー数のデータは既に書き込みされています。')


def user_timeline(api, screenname, item, count):
    '''
    ユーザーのツイート情報を取得
    ユーザー名（screenname)でツイートをサーチ
    itemにて検索個数
    いいね＋リツイートがcount以上の条件でサーチ
    '''
    tweet_data = []

    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screenname, exclude_replies=True, tweet_mode='extended',
                               lang='ja').items(item):
        if tweet.favorite_count + tweet.retweet_count >= count and 'RT @' not in tweet.full_text:
            tweet_data.append([tweet.user.name, tweet.favorite_count, tweet.retweet_count, tweet.created_at.strftime('%Y-%m-%d'),
                               tweet.full_text.replace('\n', '')])

    df = pd.DataFrame(tweet_data,
                  columns=['ユーザー名', 'いいね数', 'RT数', 'つぶやき日時', '本文'])
    df.to_csv(f'./result_userdata/{screenname}_tweet_data.csv', index=False)


def my_makedirs(path):
    '''
    データ保存用のディレクトリの作成
    '''
    if not os.path.isdir(path):
        os.makedirs(path)


def main():
    '''
    メインの実行部分
    '''
    # データを貯めていきたいユーザーIDをリストの要素として記入
    user_list = ["_whitecat_22"]

    dir_path = './result_userdata/'

    my_makedirs(dir_path)

    if not os.path.exists('./result_userdata/users.csv'):
        # 初回。データフレームを作成する。
        df_users = pd.DataFrame([user_list])
    else:
        # 一度df_usersが作られたなら、users.csvから読み込み
        df_users = pd.read_csv('./result_userdata/users.csv')

    df_users.to_csv('./result_userdata/users.csv', index=False)
    rival_list = pd.read_csv('./result_userdata/users.csv')

    API = twitter_authenticate()

    # ライバルリストからscreennameを読み込んで情報の更新
    for screenname in rival_list.loc[0]:
        print(screenname, 'の本日のフォロワー数データを作成')
        follower_transition(API, screenname)
        print(screenname, 'のツイート情報を取得')
        user_timeline(API, screenname, 10, 30)


if __name__ == '__main__':
    main()
