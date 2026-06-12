"""ログのフォーマッタ。

本番では構造化（JSON）ログ、開発では人が読めるテキストログを使う。
切り替えは settings.py の LOGGING 定義（環境変数 DJANGO_LOG_FORMAT）で行う。

詳細は docs/logging.md を参照。
"""

import datetime
import json
import logging

# 標準の LogRecord 属性。これら以外の属性は extra= で渡された追加情報とみなす。
_RESERVED = set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime", "taskName"}


class JSONFormatter(logging.Formatter):
    """LogRecord を1行の JSON に変換する（本番・ログ集約向け）。"""

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        # logger.info("...", extra={"user_id": 1}) のような追加項目を取り込む
        for key, value in record.__dict__.items():
            if key not in _RESERVED:
                log[key] = value

        return json.dumps(log, ensure_ascii=False, default=str)
