#!/usr/bin/env python3
"""
.env ファイルから Terraform 用の .tfvars ファイルを生成するスクリプト

使用方法:
    python scripts/env_to_tfvars.py

または別のディレクトリから:
    python scripts/env_to_tfvars.py --env-file /path/to/.env --output /path/to/secret.tfvars
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(
        description=".env ファイルから Terraform secret.tfvars を生成"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help=".env ファイルのパス (デフォルト: .env)"
    )
    parser.add_argument(
        "--output",
        default="terraform/secret.tfvars",
        help="出力ファイルのパス (デフォルト: terraform/secret.tfvars)"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="プロジェクトルートディレクトリ (デフォルト: 現在のディレクトリ)"
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    env_file = project_root / args.env_file
    output_file = project_root / args.output

    # .env ファイルの確認
    if not env_file.exists():
        print(f"❌ エラー: {env_file} ファイルが見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"📖 {env_file} から値を読み込み中...")

    # .env ファイルから環境変数を読み込む
    load_dotenv(env_file)

    # 必須値を取得
    required_keys = {
        "ENDPOINT": "openai_endpoint",
        "MODEL_NAME": "openai_model",
        "SUBSCRIPTION_KEY": "openai_api_key",
        "API_VERSION": "api_version",
    }

    env_values = {}
    for env_key, tf_key in required_keys.items():
        value = os.getenv(env_key)
        if env_key in ["ENDPOINT", "MODEL_NAME", "SUBSCRIPTION_KEY", "API_VERSION"]:
            if not value:
                print(
                    f"⚠️  警告: {env_key} が .env に見つかりません",
                    file=sys.stderr
                )
                if env_key in ["ENDPOINT", "MODEL_NAME", "SUBSCRIPTION_KEY"]:
                    print(f"❌ エラー: {env_key} は必須です", file=sys.stderr)
                    sys.exit(1)
                # API_VERSION はデフォルト値を使用
                value = "2024-02-15-preview"
        env_values[tf_key] = value

    # secret.tfvars を生成
    output_content = """# このファイルは scripts/env_to_tfvars.py で自動生成されました
# 手動編集は避けてください

openai_endpoint = "{endpoint}"
openai_model = "{model}"
openai_api_key = "{api_key}"
api_version = "{api_version}"
""".format(
        endpoint=env_values["openai_endpoint"],
        model=env_values["openai_model"],
        api_key=env_values["openai_api_key"],
        api_version=env_values["api_version"],
    )

    # 出力ファイルのディレクトリを作成
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # ファイルに書き込み
    with open(output_file, "w") as f:
        f.write(output_content)

    print(f"✅ 成功: {output_file} が生成されました")
    print("")
    print("📋 生成された設定:")
    print(f"  - Endpoint: {env_values['openai_endpoint']}")
    print(f"  - Model: {env_values['openai_model']}")
    print(f"  - API Version: {env_values['api_version']}")
    print("")
    print("🚀 次のコマンドでデプロイを実行してください:")
    print("  cd terraform")
    print("  terraform plan -var-file=\"secret.tfvars\"")
    print("  terraform apply -var-file=\"secret.tfvars\"")
    print("")
    print("💡 ヒント: .env ファイルを更新した場合は、このスクリプトを再度実行してください")


if __name__ == "__main__":
    main()
