"""出力フォルダ作成ユーティリティ"""

import os
from datetime import datetime, timezone, timedelta


def create_output_dir(cwd: str) -> str:
    """「出力ファイル」フォルダ内に現在時刻のサブフォルダを作成する。

    引数:
        cwd: カレントワーキングディレクトリのパス

    戻り値:
        作成されたフォルダの絶対パス
    """
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime("%Y年%m月%d日_%H時%M分")
    output_path = os.path.join(cwd, "出力ファイル", now)
    os.makedirs(output_path, exist_ok=True)
    print("出力されるファイルはここに保存：", output_path)
    return output_path
