import sys
import logging
import logging.handlers
import logging.config

#ルートロガーの作成。ログレベル=デバッグ
_root_logger = logging.getLogger('')
_root_logger.setLevel(logging.DEBUG)

#フォーマッターの作成
#コンソール用：メッセージ　を出力
_consoleFormatter = logging.Formatter(
    fmt='%(message)s'
)
#ファイル用：時刻、ログレベル、モジュール名、関数名、行番号: メッセージ　を出力
_fileFormatter = logging.Formatter(
    fmt='[%(asctime)s] %(levelname)-8s %(module)-15s %(funcName)-15s %(lineno)4s -> %(message)s'
)

#コンソール用ハンドラの作成。標準出力へ出力。ログレベル=デバッグ。書式は上記フォーマッター
_consoleHandler = logging.StreamHandler(sys.stdout)
_consoleHandler.setLevel(logging.DEBUG)
_consoleHandler.setFormatter(_consoleFormatter)

#コンソール用ハンドラをルートロガーに追加
_root_logger.addHandler(_consoleHandler)

#ファイル用ハンドラの作成。ファイル名は logging.log, ログレベル=INFO, ファイルサイズ 1MB, バックアップファイル３個まで、エンコーディングは utf-8
_fileHandler = logging.handlers.RotatingFileHandler(
    filename='logging.log', maxBytes=1000000, backupCount=3, encoding='utf-8'
)
_fileHandler.setLevel(logging.INFO)
_fileHandler.setFormatter(_fileFormatter)

#ファイル用ハンドラをルートロガーに追加
_root_logger.addHandler(_fileHandler)