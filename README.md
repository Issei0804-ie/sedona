# sedona

このシステムは DBとpythonスクリプトから構成されています。

## DBの起動方法

`　$ docker-compose up 　`

## pythonの実行方法

```buildoutcfg
python main.py dry-run      #DB更新と通知を行わない
python main.py test-server  #DBを更新し,通知を 'TEST_HOOK_URL' に行う
python main.py live-server  #DBを更新し,通知を 'LIVE_HOOK_URL' に行う
python main.py sync         #DBを更新するが,通知を行わない。
```


教務情報のRSSに数分間隔でアクセスし、新しい記事や更新された記事があるとタイトルとurlをDBに保存する。
その後は各SNSに通知を送る。

